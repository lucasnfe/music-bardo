import numpy as np
import tensorflow as tf

from gnt_utils import *

class BeamNode:
    def __init__(self, tokens, gen_ps):
        self._tokens = tokens
        self._gen_log_ps = gen_ps

    def __str__(self):
        return str(self.tokens().squeeze())

    def tokens(self):
        return self._tokens.numpy();

    def gen_ps(self):
        return self._gen_log_ps.numpy();

    def get_top_gen_sequence(self):
        max_sent = tf.argmax(self._gen_log_ps)
        return self.tokens()[max_sent]

    def forward(self, generation_params, language_model, clf_vgmidi_valence, clf_vgmidi_arousal, tokenizer):
        story_emotion = generation_params["emotion"]
        init_tokens   = generation_params["init_tokens"]
        gen_len       = generation_params["length"]
        n_ctx         = generation_params["n_ctx"]
        top_k         = generation_params["top_k"]

        # Run language_model
        generative_x = self._tokens[:, -n_ctx:]
        generative_y = language_model(generative_x, training=False)
        generative_p = tf.math.softmax(generative_y)

        # Compute sampling log probabilities
        next_beam_log_p = self._gen_log_ps + tf.math.log(generative_p)
        next_beam_log_p = tf.reshape(log_gen_ps, [-1])

        # Concatenate sequence geneeated so far with all possible tokens
        all_tokens = tf.range(generative_y.shape[-1])
        all_tokens = tf.reshape(all_tokens, (generative_y.shape[-1], 1))
        # all_tokens = tf.tile(all_tokens, tf.constant([generative_y.shape[0], 1], tf.int32))

        beam_tokens = tf.tile(self._tokens, tf.constant([generative_y.shape[-1], 1], tf.int32))

        # Run emotion model for all possibilities
        music_x = tf.concat((beam_tokens, all_tokens), axis=1)
        music_x = tf.pad(sentiment_x, tf.constant([[0, 0,], [0, gen_len - self._tokens.shape[-1]]]), "CONSTANT", constant_values=1)

        print(sentiment_x)
        quit()

        return None

def beam_search(generation_params, language_model, clf_vgmidi_valence, clf_vgmidi_arousal, tokenizer):
    n_ctx         = generation_params["n_ctx"]
    top_k         = generation_params["top_k"]
    gen_len       = generation_params["length"]
    init_tokens   = generation_params["init_tokens"]
    story_emotion = generation_params["emotion"]

    # Batchfy tokens: [beam_width, 1]
    init_tokens = tf.expand_dims(init_tokens, axis=0)

    # Get probabilities of next token
    token_p = run_language_model(init_tokens, language_model)

    # Get probabilities of next tokens being of the story emotion
    music_x = concat_all_tokens(self._tokens, generative_p.shape[-1], gen_len)
    music_valence, music_arousal = classify_music_emotion(music_x, story_emotion, clf_vgmidi_valence, clf_vgmidi_arousal)

    # Compute final log probability
    final_logp = tf.math.log(generative_p * music_valence * music_arousal)

    # Select top_k tokens to form first beam
    top_k_probs, top_k_tokens = tf.math.top_k(final_logp, top_k)
    top_probs = top_probs.numpy().squeeze()
    top_tokens = top_tokens.numpy().squeeze()

    # Reshape init_tokens and top_k_probs to be of shape (beam_width, 1)
    top_k_tokens = tf.reshape(top_k_tokens, (top_k, 1))
    top_k_probs = tf.reshape(top_k_probs, (top_k, 1))

    # Create first beam by concatenating init_tokens with the top_k tokens from the language model
    init_tokens = tf.tile(init_tokens, [top_k, 1])
    init_beam = tf.concat([init_tokens, top_k_tokens], 1)

    # Create first beam step
    c_node = BeamNode(init_beam, final_logp)
    print(c_node)
    quit()

    for i in range(init_tokens.shape[-1], gen_len):
        # Iterate on the list of adjacent nodes
        c_node = c_node.forward(generation_params, language_model, clf_vgmidi_valence, clf_vgmidi_arousal, tokenizer)
        # print(c_node)
        print(c_node.gen_ps())
        # print(c_node.sent_ps())

    print(c_node.get_top_gen_sequence())
    return c_node.get_top_gen_sequence()