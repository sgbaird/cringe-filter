<!-- cringe-lint: disable-file -->
# Scientific prose exemplars

Paragraphs from three first-author preprints written
before 2023 that are public on arXiv: the 5DOF grain boundary paper
(2021), the materials informatics review (2022), and the CrabNet and
DiSCoVeR e-print (2022). Papers are co-authored, and these were chosen
from the first-author papers written before ChatGPT, whose rates
`manuscripts_pre2023` measures. Math and cross-references were
stripped when the LaTeX was read, so a sentence may name a figure
as (X).

What to notice: "we" carries the work, a second idea gets its own
sentence rather than a colon or a semicolon, and claims are
reported with their numbers rather than sold.

6 passages, 649 words. All public.

## 172 words

> From X, we see that extraordinary predictions (definitions 1. and 2.) are commonplace due to a mixture of low number of training datapoints, simplicity of the model space (e.g. two continuous variables), and interpolative predictions. Likewise, from X and X, we see that extraordinary predictions for large number of training datapoints, complex model spaces, and extrapolative (i.e. out-of-dataset) predictions are more difficult to attain. Kauwe et al. analyzed the ability of ML models to predict extraordinary materials by holding out the top 1% of compounds for a given property and training on the bottom 99%. This was done for six different materials properties such as thermal expansion. They definitely show that extrapolation is possible, and furthermore, they show that a classification approach outperforms a regression approach. They reason that extrapolating extraordinary predictions is unlikely when the fundamental mechanism of the extraordinary prediction is different from the training dataset and that many examples of that mechanism need to be supplied. They also suggest that input data accuracy and consistency is a non-trivial issue.

<sub>https://arxiv.org/abs/2202.02380, section "An Eye Towards Extraordinary Predictions"</sub>

## 128 words

> ML techniques can be sorted into rough categories based on the size of the training data used for the model: 1 to 100, 101 to 10000, and 10000+. We demonstrate the most comprehensive set of experimentally and computationally validated examples in the literature to date and to our knowledge. Based on the distribution of techniques used in the articles, it is clear that BO and SVM are most often used for 1 to 100 and 101 to 10000 training dataset size ranges, respectively, whereas 10000+ has too few examples with too much variation to establish a trend. The low number of 10000+ validation articles relative to other size ranges illustrates the difficulty of obtaining large, high-fidelity, materials science datasets which often requires extensive curation or are simply non-existent.

<sub>https://arxiv.org/abs/2202.02380, section "Conclusion"</sub>

## 123 words

> Obtaining the training and validation data (steps 1 and 2) should be guided by materials informatics best practices. Interactively exploring the Pareto front plots can aid in the choice of hyperparameters such as the performance and uniqueness weights during validation scoring (step 3). The literature search helps in determining which compounds have already been synthesized and how, and which compounds have already been characterized and how. This helps prevent unnecessary repetition of work. Physics-based simulations (step 5) can help to eliminate candidates with unrealistically high property predictions. Synthesis, post-processing, and characterization (steps 6-8) are in a sense the pinnacle of materials discovery for practical applications. These steps appear last in part because they typically represent the highest cost-per-datapoint out of all other steps.

<sub>https://arxiv.org/abs/2203.12597, section "Results and Discussion"</sub>

## 79 words

> In prior work, a number of strategies have been developed for predicting 5DOF GB properties from experimental or simulated data. Because different works use different validation functions and data, it is difficult to objectively compare their performance. To facilitate meaningful comparisons, in addition to quoting absolute performance in terms of RMSE or MAE, we will also report the percent reduction in error compared to a constant-valued control model whose value is chosen as the mean of the respective data.

<sub>https://arxiv.org/abs/2104.06575, section "Prior Work"</sub>

## 76 words

> Many of the algorithms used for materials discovery in the literature are Euclidean-based Bayesian optimization schemes which seek a trade-off between high-performance and high-uncertainty regions, thereby favoring robust models and discovery of better candidates. These algorithms have born many fruits in materials discovery, and while high uncertainty may be correlated with novelty, they do not explicitly favor discovery of novel compounds. Additionally, novelty will likely depend heavily on both the employed distance metric and featurization scheme.

<sub>https://arxiv.org/abs/2203.12597, section "Introduction"</sub>

## 71 words

> Some have addressed the former issue of interdisciplinary expertise requirements by providing user-friendly web apps or clearly documented install and use instructions for code hosted on sites such as GitHub. An example of this was the work by Zhang et al., which used a previously constructed ML web app which takes only chemical formulas as inputs and went on to validate these predictions of low thermal conductivity for novel quaternary germanides.

<sub>https://arxiv.org/abs/2202.02380, section "Introduction to Experimental and Computational Machine Learning Validation"</sub>
