# Post-Training Open Models with Unsloth

## Introduction to Post-Training

Pre-training teaches a language model the statistical patterns of language from vast, unlabeled text corpora. The result is a *base model* — fluent and knowledgeable, but unaligned, unpredictable, and unaware of how to follow instructions or refuse harmful requests. Post-training is the family of techniques that transform this raw base model into a useful assistant.

Post-training operates on curated, task-specific data rather than random internet text. It teaches the model to respond to instructions, adopt a conversational tone, and specialize for domains like coding, mathematics, or reasoning. The dominant methods in post-training are supervised fine-tuning and reinforcement learning. Unsloth provides memory-efficient implementations of both, making it possible to fine-tune large models on consumer GPUs.

## Supervised Fine-Tuning

Supervised fine-tuning (SFT) is the simplest post-training method. You collect a dataset of high-quality `(instruction, response)` pairs and train the model to maximize the log-likelihood of the response given the instruction. Formally, the objective is:

$$
\max_\theta \sum_{(x, y) \in \mathcal{D}} \log P_\theta(y \mid x)
$$

where $x$ is an instruction or prompt, $y$ is the desired response, and $\mathcal{D}$ is the fine-tuning dataset. In practice, this means computing the cross-entropy loss only on the token positions that belong to the response $y$, not on the instruction $x$.

SFT is effective at teaching the model format, style, and shallow task-specific patterns. If your dataset consists of well-written coding examples, the model will learn to emulate that style. If your dataset consists of question-answer pairs in a specific domain, the model will learn facts from that domain.

### Why SFT is not enough

SFT is fundamentally imitation learning. The model copies the distribution of the training data. This creates three hard limits:

- **The ceiling problem**: The model cannot exceed the quality of the training data. If the human-written responses contain errors or suboptimal reasoning, the model learns to reproduce those errors faithfully. It has no mechanism to discover that a better response exists.
- **Scarcity**: Producing high-quality, expert-level responses is expensive. You can only SFT on data you can afford to label.
- **No self-evaluation**: SFT trains the model to *generate* responses, not to *evaluate* them. It never learns which of its outputs are good, which are bad, or how to improve a mediocre response. It is a generator without a discriminator.

These limits mean SFT is a necessary first step — it gives the model a sensible starting policy — but it is rarely sufficient for peak performance. The model needs a way to learn from outcomes, not just labels.

## The Need for Reinforcement Learning

Reinforcement learning addresses the ceiling problem by replacing fixed training labels with a *reward signal*. Instead of imitating a single correct response, the model explores many possible responses and learns to favour those that score highly. The reward acts as a compass, guiding the model toward behaviours that are good even if no human explicitly wrote them down.

Consider a coding task. In SFT, the model learns to reproduce the reference solution. In RL, the model can generate dozens of candidate programs, run them against a hidden test suite, and receive a reward based on how many tests pass. A response that passes all tests receives maximum reward even if it looks nothing like any training example. A response that is fluent but fails the tests receives low reward. The model learns to *solve* the task rather than *imitate* a solver.

This shift from imitation to optimization is what allows RL to push past the quality ceiling of the training data. The model can discover novel strategies, shorter proofs, more efficient code, or better phrasing by hill-climbing on the reward signal.

## RL Fine-Tuning: RLVR and GRPO

### RLVR: Reinforcement Learning with Verifiable Rewards

Traditional reinforcement learning from human feedback (RLHF) trains a separate *reward model* from human preference comparisons. The reward model learns to score responses the way humans would, and the policy model is trained to maximize that learned score. RLHF is powerful, but it inherits all the biases and noise of human judgment, and training the reward model is expensive.

**Reinforcement Learning with Verifiable Rewards (RLVR)** replaces the learned reward model with an objective, verifiable scoring function. The reward is not a neural network's opinion; it is a fact:

- For coding: the reward is the fraction of unit tests that pass.
- For mathematics: the reward is `1` if the final answer matches the ground truth, `0` otherwise.
- For game playing: the reward is the game score.
- For structured data extraction: the reward is a JSON schema validator.

Because the reward is ground-truth verifiable, there is no reward model to train, no human labeling bottleneck, and no drift from learned preference bias. The policy receives direct feedback from reality. The general RL objective becomes:

$$
\max_\theta \; \mathbb{E}_{x \sim \mathcal{D}} \left[ \mathbb{E}_{y \sim \pi_\theta(y \mid x)} \left[ R(x, y) \right] - \beta \cdot \mathbb{D}_{\text{KL}}\left( \pi_\theta \,\|\, \pi_{\text{ref}} \right) \right]
$$

Here $R(x, y)$ is the verifiable reward, $\pi_\theta$ is the policy being trained, and $\pi_{\text{ref}}$ is the reference policy (typically the SFT checkpoint). The KL-divergence penalty weighted by $\beta$ prevents the policy from drifting arbitrarily far from the reference, preserving language coherence while allowing targeted improvement.

### GRPO: Group Relative Policy Optimization

Policy gradient methods like PPO require a *value function* $V(x)$ that estimates the expected return of a given prompt. Training this value function adds memory overhead, hyperparameter sensitivity, and compute cost — burdens that are especially painful on consumer hardware.

**Group Relative Policy Optimization (GRPO)** eliminates the value function entirely. Instead of learning what a prompt is worth, GRPO computes relative quality within a *group* of responses sampled from the same prompt. For each question $x$ in the batch, GRPO:

1. Samples a group of $G$ responses $\{y_1, y_2, \ldots, y_G\}$ from the current policy $\pi_{\theta_{\text{old}}}$.
2. Computes a verifiable reward $r_i = R(x, y_i)$ for each response.
3. Computes the mean and standard deviation of rewards within the group:

$$
\bar{r} = \frac{1}{G} \sum_{i=1}^{G} r_i \qquad \sigma_r = \sqrt{\frac{1}{G} \sum_{i=1}^{G} (r_i - \bar{r})^2 + \epsilon}
$$

The small constant $\epsilon$ prevents division by zero when all rewards are identical.

4. Computes the relative advantage of each response:

$$
A_i = \frac{r_i - \bar{r}}{\sigma_r}
$$

Because advantages are centered and scaled by the group statistics, a response is good not in absolute terms but *relative to its peers*. This removes the need to estimate baseline values across the entire distribution of prompts.

5. Updates the policy via gradient ascent on a clipped surrogate objective:

$$
L(\theta) = \frac{1}{G} \sum_{i=1}^{G} \left( \min\left( \frac{\pi_\theta(y_i \mid x)}{\pi_{\theta_{\text{old}}}(y_i \mid x)} A_i, \; \text{clip}\!\left(\frac{\pi_\theta(y_i \mid x)}{\pi_{\theta_{\text{old}}}(y_i \mid x)}, 1 - \varepsilon, 1 + \varepsilon\right) A_i \right) - \beta \cdot \frac{\pi_\theta(y_i \mid x)}{\pi_{\text{ref}}(y_i \mid x)} \right)
$$

The first term inside the sum is the clipped policy-gradient surrogate, identical in spirit to PPO. The second term is the KL-penalty, estimated via the importance-weighted ratio between the current policy and the reference policy. GRPO takes the gradient of this loss with respect to $\theta$ while treating the group advantages and the old-policy probabilities as constants.

The practical benefit is enormous: no value network, no second phase of reward-model training, and lower memory usage. The cost is that reward signals must be fast to compute (unit tests, exact-match checking) because each training step evaluates $G$ sampled responses. For coding, mathematics, and rule-based games, this is exactly the right tradeoff.

## Saving the Output Model to GGUF and Using It via Ollama

After fine-tuning with SFT or GRPO, you have a Hugging Face-format checkpoint: a folder containing `config.json`, tokenizer files, and several PyTorch weight shards. This format is the lingua franca of the Hugging Face ecosystem, but it is not what Ollama consumes. Ollama expects models in the **GGUF** format, a binary specification originally developed for llama.cpp that stores quantized weights, metadata, and vocabulary in a single portable file.

The conversion pipeline is straightforward. Unsloth can export a fine-tuned checkpoint directly to GGUF, optionally applying the same quantization level you would download from Hugging Face (Q4_K_M, Q5_K_M, etc.). The export produces a `.gguf` file that contains everything needed for inference: the quantized weight matrices, the vocabulary, the rope scaling parameters, and the chat template.

Once the GGUF file exists, importing it into Ollama requires a Modelfile. The Modelfile specifies the base GGUF asset, a system prompt that defines the assistant's persona, and inference parameters such as temperature and context length. Running `ollama create` against this Modelfile registers the model in your local Ollama registry, after which it is indistinguishable from models pulled from the public Ollama Hub. You can invoke it with `ollama run`, query it through the local API, and reference it from applications using the same client libraries as any other Ollama model.

This closes the loop: you start with a pre-trained open model, fine-tune it with SFT for format and domain knowledge, push its reasoning further with GRPO and verifiable rewards, export the result to GGUF, and consume it locally through Ollama with no external API dependency.

## References

1. Unsloth. "GPT OSS (20B) Reinforcement Learning 2048 Game." Google Colab notebook, 2025. https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/gpt_oss_(20B)_Reinforcement_Learning_2048_Game.ipynb
2. Unsloth. "Qwen3 VL (8B) Vision." Google Colab notebook, 2025. https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Qwen3_VL_(8B)-Vision.ipynb#scrollTo=95_Nn-89DhsL
3. Unsloth. "Saving to Ollama." Documentation, 2025. https://unsloth.ai/docs/basics/inference-and-deployment/saving-to-ollama
4. Ollama. "Importing a GGUF-Based Model or Adapter." Documentation, 2025. https://docs.ollama.com/import#Importing-a-GGUF-based-model-or-adapter