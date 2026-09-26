<!-- cringe-lint: disable-file -->
# Exemplars: third-party

Real human-written passages, selected because their surface
statistics sit near the median for this register. Showing these
works better than describing them: in a 100-author study, directed
linguistic guidance generally performed worse than plain exemplar
prompting, and 300-word exemplars beat 50-word ones.

12 passages, 2508 words. All from public repositories.

## 1. ichesser/GB_octonion_code (2020-09-22, 329 words)

<https://github.com/ichesser/GB_octonion_code/issues/2>

> Hi Ian & Toby,    
> I've been having some issues with conversions and was hoping I get could your help.
> ## Summary
> Converting back and forth between 5DOF and octonion representations with symmetry operations results in fundamentally different GBs (likely) or suggests issue with distance calculation (less likely).
> 
> ## Starting Data
> ### cubochorically sampled octonion & symmetrically equivalent octonion
>  
> 
> ### symmetrically equivalent octonion
>  
> 
> ### calculate distance
>  
> 
> The short distance suggests o and osym represent the same GB.
> 
> ## First Conversion (octonion to 5DOF)
> ### Conversion
> See GBoct2five section at end for function
>  
> 
> ### Energies
>  
> The energy values are close, but not identical, which may indicate that the GBs are now fundamentally different.
> 
> ## 2nd Conversion (5DOF to octonion)
> ### convert back to octonions
>  
> ### calculate distance
>  
> If the grain boundaries are the same, the distance should be close to zero between them.
> 
> ## Third Conversion (octonion to 5DOF)
> ### Conversion
>  
> ### Energies
>  
> The difference in energies is the same as before within numerical precision.
> 
> ## misorientations (five / fivesym)
>  
>  
> 
> The misorientations are different, which isn't surprising.
> 
> ## disorientations (five / fivesym)
>  
>  
> 
> The disorientations are the same, which is encouraging.
> 
> ## boundary plane normals (left unchanged), (five / fivesym)
>  
>  
> 
> Since this is a low-symmetry boundary, my understanding is that there should only be an inversion center for the boundary plane normal. This seems to suggest one of two things:
> * I need to change nA simultaneously with the misorientation (i.e. there is an active rotation I'm not accounting for)
> * The "symmetrically equivalent GB" is no longer symmetrically equivalent after my GBoct2five.m routine. I'm puzzled that the grain boundary energies would be close, yet not identical.
> 
> ## GBoct2five
>  
> 
> ## Additional comments
> I wonder if these could be related to the issues Dr. Johnson ( ) had mentioned in his email concerning the conversions. I was also having trouble locating equivalent code for *GBfive2oct.m* in EMGBO or EMGBOdm to try to compare. What are your thoughts?
> 
> Thank you for the help,
> 
> Sterling

## 2. materialyzeai/megnet (2022-01-25, 381 words)

<https://github.com/materialyzeai/megnet/issues/333#issuecomment-1020867809>

> , thank you for your comments!
> 
>   I appreciate you mentioning the benefits to the field of less focus on incremental improvements in accuracy and more focus on actual materials discovery campaigns (and I would add, successful or not). I'm excited to hear about the follow-up work to BOWSR when it becomes available 🙂
> 
> Extrapolability, interpretability, and physicality. These certainly seem to be (at least a few of) the differentiators between other domains ("cats vs. dogs", Netflix movie recommenders) and materials informatics. For extrapolability, it seems like some performance metrics can be implemented such as leave-one-cluster-out cross-validation from Meredig et al., a holdout of top 1% Kauwe et al. (disclaimer: from my group), adaptive design from a list of candidates, or a made-up "ground truth" model (forgive the oximoron). For the last case, there were some interesting, limited results (in my opinion) claiming that Gaussian Process had better adaptive design results over 100 iterations than other, more accurate models (e.g. neural network ensemble and random forest, and interestingly the ground truth was chosen to be the trained neural network ensemble).
> 
> For interpretability, the more common approaches seem to be either symbolic regression or determination of feature importances based on physical descriptors.
> 
> I'm glad you bring up the physicality aspect, especially the consideration of physical laws. If you know of MatSci work that explicitly incorporates physical laws into a ML model rather than relying on physical descriptors alone, I'd be really interested to hear.
> 
> The Bartel paper and the comments in this thread have gotten me thinking about structure vs. composition more. Structure-based formation energy ML models have gotten really accurate (e.g. MEGNet and ALIGNN, down to ~ ), and like you said are "good enough" to be used in downstream practical applications. Composition-based results are (as might be expected) really poor for  , which is maybe more of an indicator of the possible wide range of   values for a given composition. BOWSR stuck out to me as a tool that could help "push the pareto front" on the trade-off between a structure- vs. composition-based materials discovery compaign, and I've been promoting it and thinking about how I might be able to use it in a more general way, i.e. "input an arbitrary composition, output a CIF".
> 
> Again, thank you for the discussion!

## 3. facebook/Ax (2023-04-20, 339 words)

<https://github.com/facebook/Ax/issues/1562#issuecomment-1515674823>

> , thanks for the cc. I'm back from a long vacation and getting back into the swing of things.
>  
> 
> I suggest using the linear equality --> linear inequality reparameterization mentioned in 
>   for ease of implementation. I compared this to the case of not implementing this reparameterization for one application (DOI: 10.1016/j.commatsci.2023.112134 or see personalized share link or the preprint). In general, implementing the linear inequality constraint improved performance. I expect that explicitly enforcing the linear equality constraint would enhance performance and improve model interpretability (i.e., the last feature also gets a feature importance), but it requires explicit use of BoTorch.
>  
>  
>  
> 
> I think objective thresholds are very important here. I suggest picking outcome constraints based on domain knowledge. These can be chosen by asking the following question for each of your objectives:
> 
> **For objective A, if all other objectives had amazing values, what is the worst allowable/viable value for objective A from an application standpoint?**
> 
> Phrased conversely, what value of objective A would make the material inviable in spite of great performance for the other objectives?
> 
> Then give yourself something like a 10% tolerance on this outcome. For example, if you're minimizing objective A, and the maximum allowable value is 1.0, then set the outcome constraint to something like $y_A \le 1.0/0.9 = 1.11$.
> 
> Pulling from the Ax multi-objective optimization tutorial:
>  
> 
> See also:
> -  
> 
> You might also consider reformulating this as a constraint satisfaction problem (constraint active search)   but I'll defer to the devs (cc  ) for whether this seems like a good fit.
>  
> 
> Seconded, but again depends on your setup. Do you mind providing some estimates of the total time and cost of running experiments with different batch sizes? The costs can be relative (e.g., 0.0 is low-cost, 1.0 is high-cost) and should incorporate the cost of the user's time. The total time refers to how long it takes to go from start to finish of the batch experiment.
> 
> Aside: asynchronous + multi-objective is non-trivial to implement   Do you have a workflow figure for the synthesis and characterization equipment?

## 4. facebook/Ax (2021-12-08, 151 words)

<https://github.com/facebook/Ax/issues/710#issuecomment-988580395>

> what is the fix you referred to? (pulling from  
>  
> 
> or
>  
> 
> Why do you think (one of these) would address the issue of symmetry that you mentioned?
>  
> 
> I'm asking because it seems relevant to a possible implementation for my use-case (  see "Components/Composition version"). I've been thinking about doing data augmentation instead, where you just supply Ax with the degenerate cases every time a new trial is added.
> 
> The number of symmetrical cases can start to get very large. In the case of   where   is the number of distinct objects:
>  
> would all be considered equivalent, meaning that   data augmentation points would be added. I'm not sure when Ax starts to get sluggish (maybe tens of thousands of points?  ), but this could be a reasonable approach when   is small (e.g.  ) and/or the initial dataset is small (~O   points) and depending on the reasonable upper limits of # points in Ax models.

## 5. siddharth-maddali/HierarchicalSmooth (2021-07-29, 176 words)

<https://github.com/siddharth-maddali/HierarchicalSmooth/issues/10#issuecomment-888711988>

> Darn..
> 
> Here are some other observations I made:
> 
> ## NodeType.txt
> It's maybe worth noting that there are 346730 nodes in ex2 and 13886 nodes in ex1.
> The unique NodeTypes are the same between the two:
>  
> The histograms of the various NodeTypes are also similar:
>  
> But there's not as many of NodeType "14"  (Quadruple Point on the outer surface) in ex2 as there are in "spiky", and more of "12".
> 
> ## SharedVertexList.txt
> In "spiky" the values are all positive. In ex2, some values are negative. I doubt this would make a difference. Just has to do with the center of the microstructure. You tried changing this and had the same issue though.
> 
> ## Other Comments
> 
> Try with a similar number of grains/resolution as in ex2. Do you get the same behavior?
> 
> Here's a look at the input microstructures:
>  
> 
> "spiky" obviously has fewer grains but the resolution is probably about the same and I don't notice anything wildly different qualitatively.
> 
>  , looks like the code works fine for the examples, but not for the data   is working with.

## 6. a-ws-m/unlockNN (2022-02-02, 86 words)

<https://github.com/a-ws-m/unlockNN/issues/37>

> I think I can appreciate that there is a decent amount of plumbing required to allow for a Keras model to be supplied and for a probabilistic one to be returned. For my own benefit, approximately how many lines of code in MEGNet would change if this was integrated directly (minimal plumbing, no testing, etc.)? The descriptions in   seemed to suggest that it was a matter of replacing the last layer with a different class. In  , could you comment on which line(s) this takes place?

## 7. ppdebreuck/modnet (2022-01-07, 76 words)

<https://github.com/ppdebreuck/modnet/issues/72>

> Google Colab notebook
>  
> 
> Works fine in VS Code on my local Windows machine, however.
>  
> It's not super important for me to get it running on Google Colab since it's running locally just fine (just tried Google Colab first), but thought I should at least share. Google searches such as:
> "pip install not finding latest version" or "pip google colab latest packages not recognized" were unfruitful for me. Might be an issue on Google Colab's side, too.

## 8. machineagency/science-jubilee (2024-06-27, 331 words)

<https://github.com/machineagency/science-jubilee/issues/125#issuecomment-2195271258>

> Thanks! That was my bad for not seeing the new user guide sooner 😅 
>  
> 
> Agreed!
>  
> 
> I think it's worth some careful thought and discussing. In one sense, when someone says "I'm committed to getting a Science Jubilee", there are up-front need to knows and things that are OK if it comes later. Hardware to purchase and build/electronics/firmware/testing instructions are the up-front need to knows I think.
>  
> 
> It's not out of question; however, in the near-term I would caution against splitting into two GitHub repos and instead focus on finding the right organization within the GitHub repo in terms of directory structure and on the website. Hardware, electronics, software, firmware, testing, documentation, and usage instructions all have some connection with each other, so splitting it up across repositories could have some unexpected downsides, especially since it wasn't designed from the start this way.
> 
> Some examples that come to mind are Pioreactor and Rodeostat. Interestingly, Pioreactor puts their CAD files on   and has a separate repo for the docs, though the website makes it feel like most things are hosted under the same blanket.
> 
> FarmBot hosts all the CAD models on OnShape, PCB Layout/schematic on a Google Drive (linked to on CAD page), and a top-level GitHub organization that hosts repositories for a web app, Python driver, Arduino firmware, etc. (i.e., anything on that organization is specific to FarmBot). They actually have an entirely separate GitHub organization dedicated to documentation with quite a few repos:  
> 
> OpenFlexure has a Gitlab organization with separation of repos:
> 
>  
> 
> Some random observations:
> - In general (not just these examples), I've noticed is that often a Web UI will be in a separate repo, perhaps because it's easy to use full-repo templates
> - Pioreactor, OpenFlexure, and FarmBot all have dedicated discourse forums
>  
>  
> 
> "So, you want to build a Science Jubilee" 😄 
>  
> 
> Similarly, as soon as we get the 3D printed parts from Lukes Laboratory, we'll be raring to go with four Science Jubilee builds with the AC summer students.

## 9. machineagency/science-jubilee (2024-06-27, 331 words)

<https://github.com/machineagency/science-jubilee/issues/125#issuecomment-2195271258>

> Thanks! That was my bad for not seeing the new user guide sooner 😅 
>  
> 
> Agreed!
>  
> 
> I think it's worth some careful thought and discussing. In one sense, when someone says "I'm committed to getting a Science Jubilee", there are up-front need to knows and things that are OK if it comes later. Hardware to purchase and build/electronics/firmware/testing instructions are the up-front need to knows I think.
>  
> 
> It's not out of question; however, in the near-term I would caution against splitting into two GitHub repos and instead focus on finding the right organization within the GitHub repo in terms of directory structure and on the website. Hardware, electronics, software, firmware, testing, documentation, and usage instructions all have some connection with each other, so splitting it up across repositories could have some unexpected downsides, especially since it wasn't designed from the start this way.
> 
> Some examples that come to mind are Pioreactor and Rodeostat. Interestingly, Pioreactor puts their CAD files on   and has a separate repo for the docs, though the website makes it feel like most things are hosted under the same blanket.
> 
> FarmBot hosts all the CAD models on OnShape, PCB Layout/schematic on a Google Drive (linked to on CAD page), and a top-level GitHub organization that hosts repositories for a web app, Python driver, Arduino firmware, etc. (i.e., anything on that organization is specific to FarmBot). They actually have an entirely separate GitHub organization dedicated to documentation with quite a few repos:  
> 
> OpenFlexure has a Gitlab organization with separation of repos:
> 
>  
> 
> Some random observations:
> - In general (not just these examples), I've noticed is that often a Web UI will be in a separate repo, perhaps because it's easy to use full-repo templates
> - Pioreactor, OpenFlexure, and FarmBot all have dedicated discourse forums
>  
>  
> 
> "So, you want to build a Science Jubilee" 😄 
>  
> 
> Similarly, as soon as we get the 3D printed parts from Lukes Laboratory, we'll be raring to go with four Science Jubilee builds with the AC summer students.

## 10. anthony-wang/CrabNet (2022-01-07, 114 words)

<https://github.com/anthony-wang/CrabNet/issues/10#issuecomment-1007145550>

> , looks like MODNet implemented multi-class classification. Sounds like they just replaced a softmax activation function with a sigmoid. See   In particular, see the changes in  . They use   and   instead of  , and pass in something to   as shown here. I'd have to dig a bit deeper (in reality, shallower in terms of MODNet's stack trace) to see how they use the sigmoid, but I imagine that for 20 possible labels, they just divide the sigmoid into 20 equal segments and find which bin it fits into. Let me know if you need help with this. If you open up an issue with MODNet asking about it, they would probably help out, too.

## 11. anthony-wang/CrabNet (2022-01-07, 114 words)

<https://github.com/anthony-wang/CrabNet/issues/10#issuecomment-1007145550>

> , looks like MODNet implemented multi-class classification. Sounds like they just replaced a softmax activation function with a sigmoid. See   In particular, see the changes in  . They use   and   instead of  , and pass in something to   as shown here. I'd have to dig a bit deeper (in reality, shallower in terms of MODNet's stack trace) to see how they use the sigmoid, but I imagine that for 20 possible labels, they just divide the sigmoid into 20 equal segments and find which bin it fits into. Let me know if you need help with this. If you open up an issue with MODNet asking about it, they would probably help out, too.

## 12. blaiszik/Materials-Databases (2023-05-15, 80 words)

<https://github.com/blaiszik/Materials-Databases/issues/4#issuecomment-1548324206>

> I just noticed the last commit is 8 years ago. Surprising how many platforms were out there nearly a decade ago! If either of us get the opportunity to write a review that has a focus or section on materials databases, that might be a good time to convert and update this, and provide a link to it in the paper as an ongoing list (especially with community contributions).
> 
> I'm planning to do the same with the low-cost SDL manuscript.

