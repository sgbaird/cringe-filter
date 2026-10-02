<!-- cringe-lint: disable-file -->
# Exemplars: tutorial

Passages from docs pages, READMEs and tutorial notebooks in public
repositories, picked by hand. Each comes from its file as it stood
before 2023, when no one but the writer had committed to it. Code
blocks, tables and images are left out, and links keep their text but
not their URLs.

9 passages, 1754 words.

## 1. sparks-baird/self-driving-lab-demo (2022-10-16, 299 words)

<https://github.com/sparks-baird/self-driving-lab-demo/blob/24c9a8622a4e75f90ed1678a7e8d40b62685a950/notebooks/6.2-multi-fidelity.ipynb>

> In the previous notebook, we covered multi-objective optimization: i.e. looking at
> optimal tradeoffs between multiple, sometimes competing, objectives. Here, we'll take a
> look a multi-fidelity optimization. First, let's start off by loosely defining a
> fidelity parameter as a parameter that controls the quality of the information being
> obtained. For example, in a finite element modeling simulation, a coarse grid spacing
> might result in a large amount of noise or bias. We refer to this as low-fidelity.
> Likewise, a finer grid spacing will likely result in much less noise - hence,
> high-fidelity. Situations such as these are typically referred to as continuous fidelity
> parameters.
>
> Similarly, there exists discrete, categorical fidelity parameters. For example, a thorough
> experiment performed in a wetlab is considered higher-fidelity than a corresponding
> simulation because the experiment by definition is meant to be more representative of
> reality. The phrase "experimental validation" comes to mind in this context. Likewise,
> we could have multiple types of instruments that measure the same property, but at
> different resolutions and therefore at different fidelities. Multi-fidelity optimization
> should be used when increasing/decreasing a parameter is known to result in more
> trustworthy data. See also discussion about multi-task vs. multi-fidelity optimization.
>
> For the demo, we have two notions of fidelity parameters that we can explore:
> - Integration time as an analytic function of `atime` and `astep`, where longer
>   integration times result in less noise, and thus higher fidelity (continuous fidelity
>   parameter, though technically discrete since there are a limited number of choices)
> - Simulated spectrum vs. experimental spectrum (discrete, categorical fidelity parameter)
>
> We'll explore both in the following two notebooks. We will limit ourselves to single-objective
> optimization; however, I plan to cover scenarios that incorporate multiple advanced
> topics in a single optimization task: multi-objective, multi-fidelity, high-dimensional,
> constrained, and asynchronous or batch optimization. Stay tuned!

## 2. sparks-baird/self-driving-lab-demo (2022-08-30, 297 words)

<https://github.com/sparks-baird/self-driving-lab-demo/blob/c7f04472aa3fce9f8646fb2472f578a2e0eb4f0e/notebooks/2.2-sensor-simulator.ipynb>

> To help troubleshoot the source of the unexpected
> behavior, we'll move the schedule up and use a simulator. The large stochasticity for
> identical inputs shown at the end of the last notebook is a cause for concern.
>
> Is the stochasticity due to excessive noise from too short of integration time or is it
> a problem with the hardware such as a sensor malfunction? Based on inspection from my
> own eyes, fixed inputs appeared to produce very similar colors. Last, this could be due
> to (intentional) naive design decision of starting out with mean absolute error for the
> objective function rather than something more tuned to this problem, such as Wasserstein
> distance between the two discrete spectra. In reality, it's probably some mix and
> interplay of the previous issues:
>
> - **(epistemic) uncertainty**
>   - i.e. just a part of the system, solved by a longer integration time (more data)
> - **sensor malfunction/degradation**
>   - due to blasting it repeatedly with a bright DotStar
>   - and/or hard device resets due to system crashes
>   - and/or or (just remembered!) a series
>   of recent unexpected power outages for my housing community
> - **Poorly defined objective function**
>   - It was defined in a way that it doesn't handle stochastic bias when
>   a signal is measured in an adjacent channel, solved by using a robust distance metric
>   for discrete distributions (e.g. Wasserstein)
> - **Something else?**
>
> My wife kindly reminded me of past lessons learned during experimentation, and
> encouraged me to try out the simulation. So, let's do that here! We'll take a look at
> our domain knowledge / assumptions for the simulation, briefly describe the approach,
> and then dig into a snapshot of the `SensorSimulator` class. Finally, we'll demonstrate
> the usage and run our grid vs. random vs. Bayesian search algorithm comparison with our
> simulation.

## 3. sparks-baird/self-driving-lab-demo (2022-11-02, 167 words)

<https://github.com/sparks-baird/self-driving-lab-demo/blob/de24ffb605919a8d04bcb2e46fa68278893464df/notebooks/README.md>

> This is a collection of tutorial notebooks and demonstrations for the
> self-driving-lab-demo! These notebooks will start by going over the hardware basics of the LEDs and
> sensor (`Blinkt! Getting Started`) and testing out different search algorithms with the bonus of
> designing a simulation (`Search Algorithms using Blinkt!`). Rather than edit the notebooks ad-hoc when
> something goes wrong, it can be more instructive to see the behind-the-scenes
> development process, mistakes and all! Not every mistake will be instructive, so I try
> to leave only the ones that teach important principals related to self-driving
> laboratories such as validating results and troubleshooting software-hardware
> interfacing. Next comes the use of the PicoW-SDL-Demo via hosting a local web server (`Pico W / MicroPython implementation`) and
> then using Internet-of-things-style communication to remotely control the PicoW
> (`Controlling the Pico W Remotely (IoT-style)`). There is also a notebook on controlling
> the Pico using a nonwireless option (i.e. compatible when WiFi is not available /
> difficult to connect to or when nonwireless Pico is being used).

## 4. sparks-baird/mat_discover (2022-12-17, 194 words)

<https://github.com/sparks-baird/mat_discover/blob/6889cae51c13a18b7d2663b5ff07b3433234fe0d/docs/source/readme.md>

> The primary anticipated use-case of DiSCoVeR is that you have some training data (chemical formulas and target property), and you would like to determine the "next best experiment" to perform based on a user-defined relative importance of performance vs. chemical novelty. You can even run the model without any training targets which is equivalent to setting the target weight as 0.
>
> ### Is it any good?
>
> Take an initial training set of 100 chemical formulas and associated Materials Project bulk moduli followed by 900 adaptive design iterations (x-axis) using random search, novelty-only (performance weighted at 0), a 50/50 weighting split, and performance-only (novelty weighted at 0). These are the columns. The rows are the total number of observed "extraordinary" compounds (top 2%), the total number of _additional_ unique atoms, and total number of additional unique chemical formulae templates. In other words:
> 1. How many "extraordinary" compounds have been observed so far?
> 1. How many unique atoms have been explored so far? (not counting atoms already in the starting 100 formulas)
> 1. How many unique chemical templates (e.g. A2B3, ABC, ABC2) have been explored so far? (not counting templates already in the starting 100 formulas)

## 5. sparks-baird/xtal2png (2022-07-08, 134 words)

<https://github.com/sparks-baird/xtal2png/blob/0b4667a01da9944bc9786560a4098d8df5985c84/docs/index.md>

> The latest advances in machine learning are often in natural language such as with long
> short-term memory networks (LSTMs) and transformers or image processing such as with
> generative adversarial networks (GANs), variational autoencoders (VAEs), and guided
> diffusion models; however, transfering these advances to adjacent domains such as
> materials informatics often takes years. `xtal2png` encodes and decodes crystal
> structures via grayscale PNG images by writing and reading the necessary information for
> crystal reconstruction (unit cell, atomic elements, atomic coordinates) as a square
> matrix of numbers, respectively. This is akin to making/reading a QR code for crystal
> structures, where the `xtal2png` representation is invertible. The ability to feed these
> images directly into image-based pipelines allows you, as a materials informatics
> practitioner, to get streamlined results for new state-of-the-art image-based machine
> learning models applied to crystal structure.

## 6. sparks-baird/mp-time-split (2022-08-06, 124 words)

<https://github.com/sparks-baird/mp-time-split/blob/a38ee688e30dd8abeb9906e34b26be8ac06f9781/README.md>

> While methods for cross-validating accuracy of materials informatics models is well
> estabilished (see for example Matbench),
> evaluating the performance of generative models such as
> FTCP or
> imatgen, and many
> others is less
> straightforward. Recently, Xie et al. introduced new
> benchmark datasets and metrics in CDVAE for several
> state-of-the-art algorithms. This repository acts as a supplement to CDVAE benchmarks,
> delivering a new benchmark dataset (`Materials_Project_Time_Split_52` or **MPTS-52**) with time-based (5 $\times$ train/val)
> +train/test splits suitable for cross-validated hyperparameter optimization and
> subsequent benchmarking via the test split.
>
> **MPTS-52** is most comparable to **MP-20**
> from Xie et al., with the difference that up to 52
> atoms are allowed and possibly a difference in the unique elements, as no elemental
> filtering was applied (e.g. removal of radioactive elements).

## 7. sparks-baird/mete-3070 (2021-08-27, 161 words)

<https://github.com/sparks-baird/mete-3070/blob/d54f9a37de4bc9de42f8c39e10b9031be40de4d1/README.md>

> Creating a new environment gives you a clean slate that won't mess with other projects. The GUI instructions for creating a new environment are:
>
> `Environment` tab --> `Create` --> enter `Name` (e.g. `mete-3070`) --> Choose `Python 3.8` --> `Create`
>
> To switch to your new environment:
>
> `Home` tab --> `Applications on ...` --> Click dropdown arrow and select `mete-3070` (or whatever you named your environment)
>
> ### Install Dependencies
> To install the dependencies we'll be working with:
>
> `Install` (see button within either Powershell Prompt or CMD.exe Prompt widget) --> `Launch` (again, either Powershell or CMD.exe) --> type the following command followed by the return key `conda install numpy scipy matplotlib`. Note that these are the dependencies for "Module 1", and other packages may be necessary as the course progresses.
>
> To install Jupyter Notebook, click the `Install` button within the Jupyter Notebook widget.
>
> Click `Launch` inside the Jupyter Notebook widget, navigate to a directory of your choice, and then `New` --> `Python 3` (Notebook).

## 8. sparks-baird/auto-paper (2021-10-14, 180 words)

<https://github.com/sparks-baird/auto-paper/blob/1b8580adec728e519422467c1534988c7d72a943/matlab/README.md>

> MATLAB Central has useful things like Answers (how do I ...?) and File Exchange (has someone already written & packaged the piece of code you're trying to write?). Google searches with the keyword "matlab" will often pull up links to MATLAB Answers and the MATLAB File Exchange (abbreviated to FEX). Login to your MathWorks account and bookmark questions as you go.
>
> There is a possibility that for whatever you're trying to do, a built-in MATLAB function or a function written by someone else already exists. Keep that in mind as you balance the time to search for existing code vs. writing your own.
>
> I also recommend keeping a record of answers that you find on MATLAB Central or otherwise (I use OneNote, in which case I suggest having a separate section for each language or program, and a single page for each topic or title). Include both the link and a (preferably text) snippet of the relevant code that was useful. I both update and reference my personal record frequently (often daily) for MATLAB, Mathematica, git, python, bash, Excel, etc.

## 9. sgbaird/TeXport (2021-10-27, 198 words)

<https://github.com/sgbaird/TeXport/blob/f5c8fdee17e963b8f73a313d81742c3f1d7e47ce/README.md>

> If you're new to Mathematica altogether, start with the Documentation Home and look at the linked Working in Notebooks. If you're less familiar with typesetting equations in Mathematica, start by reading this typesetting guide, then in a Mathematica notebook, go to:
> `Menu Bar --> "Palettes" --> "Basic Math Assistant"`.
> Hover over the various boxes to see the corresponding shortcuts. I recommend using the shortcuts for efficiency, but you can also click on the boxes. If you're interested in the inner-workings of the code, see also String Manipulation Guide. The Mathematica Stack Exchange is another great resource, and many Google searches will direct you to there.
>
> ## Advanced
> You can also perform symbolic computations for a proof and export the entire proof with intermediate commentary as a `.tex` file. I have done this for a paper I'm working on and will probably put an example together for this. Open up an issue if you'd like to see this sooner.
>
> ## LaTeX
> Once you have your equation `.tex` files (I suggest putting these in an "equations" folder in your paper repo), commit and push them, and reference the equations in the LaTeX body using e.g. `\cref{eq:svd-force}` from the `cleveref` package.
