<!-- cringe-lint: disable-file -->
# Exemplars: github-long

Real passages Sterling wrote, selected because their surface
statistics sit near the median for this register. Showing these
works better than describing them: in a 100-author study, directed
linguistic guidance generally performed worse than plain exemplar
prompting, and 300-word exemplars beat 50-word ones.

12 passages, 2564 words. All from public repositories.

## 1. AccelerationConsortium/ac-dev-lab (2025-01-14, 192 words)

<https://github.com/AccelerationConsortium/ac-dev-lab/issues/148>

> Linear actuator without position feedback makes it harder to integrate into SDLs. I.e., "send the command into the void and hope it did what you were hoping for". The position feedback can help with controlling speed, synchronizing with other actuators, testing for failure conditions (trying to get it to a particular place but it won't go there, indicating some kind of issue). We have a:
> - 16-P Miniature Linear Actuator with Feedback 100mm 150:1 12 volts ( )
> 
> In the case of   the intention was to be able to have precise syringe pressure vs. actuator position measurements.
> 
> Details about and an intro to the linear actuator control (LAC) board are available at   (EDIT: there's also an actuonix arduino guide that will help with microcontroller usage with a Pico W)
> 
>   could you describe what you tried? I can ask someone to continue the troubleshooting if needed.
> 
> You also mentioned a voltage booster. We were using a 5V to 6V converter for the original actuator. Technically I think it actuates with only 5V, though better to supply 6V via the booster. We also have some 6V power supplies too I think. More context here:

## 2. ichesser/GB_octonion_code (2020-09-22, 329 words)

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

## 3. materialyzeai/megnet (2022-01-25, 381 words)

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

## 4. AccelerationConsortium/ac-dev-lab (2025-04-01, 151 words)

<https://github.com/AccelerationConsortium/ac-dev-lab/issues/132#issuecomment-2770803905>

> Major question: to try to adhere, mount to SEM externally (e.g., a base that wraps around), or modify the SEM with some mounting holes or similar. Whether to mount it to the side, the top, or have it pull out from ahead of it (i.e., mounted separately, relying on weight of the SEM to keep the SEM in place). Can't mount internal to chamber because of outgassing of plastic/etc.
> 
> Will want to do a force test of some kind to get a sense of what's needed to open and close the door. I think one of the SDLs has done something loosely like this (Maybe SDL2?).
> 
> I lean a bit towards using a strong adhesive initially, and knowing what's needed to remove/dissolve the adhesive. 
> 
> EDIT: the weight of the machine can be leveraged, I'm picturing a really wide shallow square U shaped bracket going underneath the machine. No direct mechanical connection

## 5. facebook/Ax (2023-04-20, 339 words)

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

## 6. PrefectHQ/prefect (2025-08-22, 172 words)

<https://github.com/PrefectHQ/prefect/discussions/16467#discussioncomment-14191740>

> , I often hesitate between going to slack vs. gh discussion (originally the forum). In particular, I might want to use Marvin and potentially get quicker responses on slack, but it becomes harder to find later (less searchable) and is non-provenant, due to Slack's 90-day "hiding" policy for free-tier slack accounts (makes sense, there's 17k people on the slack). So, if I try to link to one of those messages, I won't be able to view it after it becomes hidden at 90 days. On the other hand, discussions are more provenant and have other bells and whistles associated with GitHub, but might be less amenable to quick, short-form interactions.
> There is a "save thread to discourse" slack app integration, which is now non-functional. Would it be possible to migrate this to open a pre-filled discussion? This would help me avoid needing to copy each individual message over, as well as having to deal with the fact that formatting gets mostly lost when manually copy-pasting from slack.
> (example thread, posted on 2025-08-22)

## 7. facebook/Ax (2021-12-08, 151 words)

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

## 8. vertical-cloud-lab/tensegrity-optimization (2026-05-15, 158 words)

<https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/52#issuecomment-4462368734>

> +claude-opus-4.7 noting that when it's vertically oriented, of course it's going to be fine if we leave a large enough gap. What we're worried about it when it's oriented horizontally, so it's essentially intentional spaghetti / stringing (but with a very low distance for it to drop) in the case of an air gap. Also, we don't have any PVA (and you're mistaken, there's no 3rd nozzle in the H2D, just that the Bambu Lab AMS Pro 2 has 4 slots for different types of filaments). So your current set of designs doesn't help us. Focus on the air gap for different air gap sizes and different joint sizes. Also, you made a mistake using the ball shape. What I actually want to use is "A3 countersunk — 90° cone mating a countersink in the +X face → flush, self-centring, ~8.8 mm² conical wall" (originally I specified A1, but I think this A3 from   makes more sense perhaps)

## 9. sgbaird/LatticePlane (2022-11-05, 151 words)

<https://github.com/sgbaird/LatticePlane/issues/2>

> Without   (which is how it was before I tried resolving a bug #1):
>  
> Upon further inspection, this was due to the intersection being incorrectly determined as a line instead of a plane AFAIK. Adding   seemed to resolve this issue for   (Al), but now the results for   (Fe3C) are off (maybe they're off for   since I didn't do manual verification of the values). The   function isn't even working because all of the intersection areas were determined to be zero for Fe.
> 
> This is running on Mathematica 13.0.1.0 on Microsoft Windows 64-bit.
>  
> 
> Getting the plane intersection functions to be robust across a variety of use-cases has been very difficult, and if I'm not mistaken, somewhere between 12.2 and 13.0 there's a bug that has been introduced. Haven't verified by reverting to 12.2.
> 
> The issue might also be with how the intersections between the bounded plane and the atom hard spheres are being computed.

## 10. vertical-cloud-lab/byu-vcl (2026-02-28, 199 words)

<https://github.com/vertical-cloud-lab/byu-vcl/issues/40#issuecomment-3975910510>

> Thanks!
> 
> What is the frame rate for the one you shared? Every 10 seconds or so I'm guessing? What are the limits on the app you downloaded vs. the native camera app?
> 
> This one is a bit nuanced. I think we'll want one camera to be a whole lab time lapse, regardless. I found that trying to post-process large amounts of video to turn it into a time lapse is significantly harder than just taking a time lapse from the beginning on a phone. Since we have three phones, it might be worth having one be a time lapse that's running semi indefinitely, one that is doing a stream meant to run indefinitely, and one that we use for SOP recording. I'm less concerned about the the one that does a continuous live stream because there's no easy way to stop and restart it every 8 hours, which would be required if we wanted to store all the videos. This is part of why the pi camera live streaming setups are unique and appealing. The software is set up to stop and restart streams every 8 hours and is tolerant to failures if a stream dies for some reason.

## 11. AccelerationConsortium/echem-cell (2025-08-12, 165 words)

<https://github.com/AccelerationConsortium/echem-cell/issues/3#issuecomment-3179572430>

> Swapping out the tubing won't be an issue for the other ones (for the adafruit and pioreactor ones, no tools needed, there's a clip that you pop off), but the tubing will need to be compatible in terms of dimension / compression. I.e., it needs to be able to fit, and pressing it with the rollers needs to be able to seal/pinch it. Peristaltic pumps only really work with flexible tubing. I'm not as familiar with multi-roller pumps, but what's mentioned about less pulsating makes sense and I imagine it might address other issues like allowing for a broader range of tube sizes and ensuring a tight seal. Otherwise, I think you'll need to look at a syringe pump designed for aggressive chemicals.
> 
> PWM will be easy. RS485 will be a bit more difficult, but still possible. If you search for RS232 and RS485 on the AC training lab issues you should be able to find some of those threads. Happy to support on this.

## 12. siddharth-maddali/HierarchicalSmooth (2021-07-29, 176 words)

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

