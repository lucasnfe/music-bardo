import numpy as np
import tensorflow as tf
import clf_vgmidi.midi.encoder as me

from gnt_utils import *

def baseline(generation_params, idx2token):
    story_emotion  = generation_params["emotion"]
    vgmidi         = generation_params["vgmidi"]
    gen_len        = generation_params["length"]
    prev_piece     =  generation_params["previous"]

    pieces_with_story_emotion = []
    for piece, emotion in vgmidi:
        if (np.array(emotion) == discretize_emotion(story_emotion)).all():
            pieces_with_story_emotion.append((piece, emotion))

    print("Found", len(pieces_with_story_emotion), "with emotion", discretize_emotion(story_emotion))

    if prev_piece:
        prev_ix, prev_token = prev_piece 
    else:
        prev_token = 0
        prev_ix = np.random.randint(len(pieces_with_story_emotion))

    selected_piece, _ = pieces_with_story_emotion[prev_ix]

    generated_piece = []
    
    total_duration = 0
    while total_duration <= gen_len:
        generated_piece.append(selected_piece[prev_token])

        generated_text = " ".join([idx2token[ix] for ix in generated_piece])
        total_duration = me.parse_total_duration_from_text(generated_text)

        prev_token += 1

    return generated_piece, generated_text, (prev_ix, prev_token)