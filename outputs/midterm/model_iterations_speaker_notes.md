# Slide 8 - Iterations After M2BERT Pretraining

After switching to pretrained M2BERT, I tested several ways to adapt it.

One pitch continuation reached 62.53 percent at epoch five. A separate longer run stayed below its starting checkpoint.

I added duration correction, then trained pitch and duration together. The joint model reached 62.12 percent for pitch and 87.78 percent for duration from one checkpoint.

For accidentals, I added rare-class examples. Macro F1 rose from 0.512 to 0.542, with a small drop in overall accuracy.

Then I focused on pitch context. Training the backbone and context branch together reached 63.73 percent. Freezing the backbone and training only the branch reached 64.73 percent. Caching the backbone outputs made those experiments much faster. A longer-budget version reached 64.93 percent, with its best checkpoint at epoch two.

I also trained a top-five reranker using interval, register, and harmony features. Both early stopping and a full ten-epoch run gave no improvement.

Finally, I doubled target examples to 19,996 and tested frozen and unfrozen backbones. Those runs stayed below the starting model, so I kept the frozen backbone with context v3.
