<!-- cringe-lint: disable-file -->
# Exemplars: discussions

Real human-written passages, selected because their surface
statistics sit near the median for this register. Showing these
works better than describing them: in a 100-author study, directed
linguistic guidance generally performed worse than plain exemplar
prompting, and 300-word exemplars beat 50-word ones.

12 passages, 2111 words. All from public repositories.

## 1. PrefectHQ/prefect (2025-08-22, 172 words)

<https://github.com/PrefectHQ/prefect/discussions/16467#discussioncomment-14191740>

> , I often hesitate between going to slack vs. gh discussion (originally the forum). In particular, I might want to use Marvin and potentially get quicker responses on slack, but it becomes harder to find later (less searchable) and is non-provenant, due to Slack's 90-day "hiding" policy for free-tier slack accounts (makes sense, there's 17k people on the slack). So, if I try to link to one of those messages, I won't be able to view it after it becomes hidden at 90 days. On the other hand, discussions are more provenant and have other bells and whistles associated with GitHub, but might be less amenable to quick, short-form interactions.
> There is a "save thread to discourse" slack app integration, which is now non-functional. Would it be possible to migrate this to open a pre-filled discussion? This would help me avoid needing to copy each individual message over, as well as having to deal with the fact that formatting gets mostly lost when manually copy-pasting from slack.
> (example thread, posted on 2025-08-22)

## 2. AccelerationConsortium/ac-microcourses (2025-04-18, 95 words)

<https://github.com/AccelerationConsortium/ac-microcourses/discussions/159#discussioncomment-12873809>

> Im wondering if the insert.py is reflecting the newest version. In particular, pymongo can't be used within MicroPython. Can you commit your latest files and include a link to your assignment repo here so I can check?
> I haven't seen this error before, but it may be related to storage space on your microcontroller. Could you try deleting all files on it (except maybe your HiveMQ certificate so you don't have to regenerate it) and reuploading the necessary ones for module 5?
> If that doesn't work, could you also try reflashing MicroPython onto the microcontroller?

## 3. community/community (2025-05-31, 91 words)

<https://github.com/orgs/community/discussions/161190>

> Why are you starting this discussion?
> Bug
> What GitHub Actions topic or product is this about?
> Workflow Deployment
> Discussion Details
> I've been struggling to get Copilot to run pre-commit successfully. The issue seems to be during the initialization of the environment. I've tried a number of different ways and prompts, including adding it to the copilot setup instructions, without luck.
> Most recent, in-depth example: AccelerationConsortium/ac-dev-lab#297
> (And the action:  
> Example where putting it in copilot setup steps produced a non-informative error:
> 
> AccelerationConsortium/ac-dev-lab#297
> corresponding action:  
> 
> precommit run --all-files does fine on a codespace.

## 4. emdgroup/baybe (2025-05-02, 534 words)

<https://github.com/emdgroup/baybe/discussions/545#discussioncomment-13017302>

> Trivial/Global early stopping ...
> 
> 
> E.g., for trial-level stopping, someone is growing cells and monitoring a certain metric over time. Similarly for waiting for separation with liquid-liquid extraction. Sometimes, they'll want to kill the experiment early, but still learn from that info. Likewise applicable for other types of time-series-like data.
> 
> 
> Cardinality with auto-diff: yes, we plan to extend that framework but please note that even the current framework probably does more than what you've described. In fact, we're not brute-forcing a specific candidate set – instead, we only consider a finite set of (in-)activity assignments of the parameters. But for each of these assignments, an actual auto-diff based optimization is conducted 👍🏼
> 
> 
> Ah, interesting - could you point me to where I could look at this?
> 
> 
> High-dimensional BO: yes, absolutely on the list. First, by incorporating the Hvarfner priors, and second by enabling specific algorithms for it.
> 
> 
> 👍🏼
> 
> 
> Analytical outcomes/objectives: ...
> 
> 
> Cool! A simple example is material cost which is usually an analytical outcome (known, deterministic, not black-box).
> 
> 
> Arbitrary constraints: yes, on the roadmap, but with a little lower prio at the moment
> 
> 
> On a related note, I'm curious, how are the linear composition constraints implemented?   -->   -->   --> 
>   
>     
>       baybe/baybe/constraints/continuous.py
>     
>     
>          Line 33
>       in
>       b060cff
>     
>   
>   
>     
> 
>         
>           
>            class ContinuousLinearConstraint(ContinuousConstraint): 
>         
>     
>   
> 
>  (any suggestions on where to go from here to see how it gets passed to BoTorch?)
> 
> 
> Hybrid constraints: no concrete plans here, partly because we haven't even had a use case for it so far. If you have one that you could share, I'd be very much interested 🙃
> 
> 
> Ah, I think I misunderstood originally, somehow misinterpreted this. To clarify, discrete constraints and continuous constraints can be implemented within the same campaign, independently? (Agreed about a single constraint involving both being an edge case)
> 
> 
> Custom surrogates: Please note that we have taken care to make customization easily possible for some parts of the framework – surrogates are one of them, because we already anticipated that people might want to use their proprietary models. So yes: we have clear API defined for this in form of a lightweight protocol, to let users specify their own logic. As long as you obey to it, you can use whatever surrogate you like. Does this answer the question, though? 🤔 Writing a customization guide for our user guide is overdue 😬
> 
> 
> Nice! I think this addresses the question, so as long as one can provide a sampling method, it should be compatible?
> 
> 
> Visualizations are still not a focus area, but I wouldn't object against having some basic methods in place as long as they are generic enough to cover many use cases. Can you tell me what is it that you're hoping for?
> All good - as you mentioned previously, exposing things like inverse lengthscales, model predictions and uncertainties, and optimization traces makes it easy for others to create visualizations. There are a number of visualizations that I tend to use, some shown in  
> Multi-fidelity: yes, shouldn't be too far down the road 👍🏼
> Nice!
> 
> 
> As an aside, I don't remember if this was here the last time I looked (great to see the trajectory of improvements to the already very good docs), but I'm noticing the non-comprehensive overview on the front page:

## 5. sparks-baird/self-driving-lab-demo (2022-10-29, 149 words)

<https://github.com/sparks-baird/self-driving-lab-demo/discussions/117>

> One idea I've had is to create a notebook that does a walk-through of setting up a free SQL database (e.g.   and using Ax's SQL backend for storing experiments. I think it would also be informative to have similar notebooks focused on storing experimental data to other platforms: MongoDB Atlas, Foundry, Figshare or Zenodo, and Matminer.
> EDIT: See   for info on the free-tiers of different cloud services.
> Related:
> 
> #84
> #91
> #122
> 
>   curious to hear your thoughts.
> EDIT: I've been using MongoDB with the shared tier. It gets pretty expensive moving to a serverless option if using find_one without an index   so it would likely be much better to avoid serverless and just choose the appropriate shared or dedicated cluster options.
> EDIT: DynamoDB is another option. See comparisons/limitations at   (in particular, max 400 kB vs. 16 MB per document, though much more data storage allowed (25 GB vs. 500 MB)

## 6. sparks-baird/self-driving-lab-demo (2022-08-13, 307 words)

<https://github.com/sparks-baird/self-driving-lab-demo/discussions/59#discussioncomment-3615629>

> The discussion with Helen Leigh from Crowd Supply:
> 
> Additionally, you may wish to reconsider building your device around the RPi 4, since they are currently very difficult to find right now, with no signs of the situation getting better in the near future. Unless you have a really great connection at RPi, it is very unlikely that you will be able to get enough RPi 4s to fulfill a campaign.
> 
> That's a good point about the RPi 4. I think I'll try to build the system around a Pico W with ML training/decision-making happening externally. Though, there is definitely the appeal of having some reasonable compute power to run more expensive ML algorithms on the RPi 4 for decision-making (i.e. make it a truly standalone system). Open to suggestions for other single-board computers than the RPi 4 if you have any (still with "reasonable" compute power). Of course, I can look at articles like   but it's tough to know what might be a better alternative for this specific project where ease-of-use is a high priority.
> ...
> Do you think redesigning for the Pi Zero 2 W (or Pi Zero W) would be a suitable replacement for the RPi 4 or do you think I'll need to design for a different ecosystem altogether (e.g. Arduino)? Any recommendations for what I should look into?
> 
> The Pi Zero is also out of stock everywhere due to the chip shortage. You can find them for sale on ebay and amazon for $90+. I don't think it would have enough computing power for your project anyhow. The only RPi products reliably in stock are based on the RP2040, which you can still buy (this is why there are a million RP2040 projects right now!).
> 
> 
> Take a look at the BeagleBoard range for an alternative SBC ecosystem   They are open source hardware too.

## 7. AccelerationConsortium/ac-microcourses (2024-07-22, 73 words)

<https://github.com/AccelerationConsortium/ac-microcourses/discussions/26#discussioncomment-10119302>

> If the only difference is the use of pytest vs. running orchestrator.py directly, and the pytest error occurs before any light-mixing experiments start, it is likely an issue I'll need to debug. One last thing - do you mind running microcontroller.py and then triggering the autograding? (E.g., add an extra space to a file), then include the link to the GitHub actions workflow here?
> This would help me to reference the full example.

## 8. sgbaird/honegumi (2023-06-28, 60 words)

<https://github.com/sgbaird/honegumi/discussions/2#discussioncomment-6301573>

> Exposing as a PyScaffold extension
> Perhaps as a separate package.
> 
> put the notebooks into the notebooks folder, unit test(s) associated with that notebook into the tests folder, tables into the data folder (if applicable), make a copy of dependencies (loose and strict), etc.
> Should there be an option to add new tutorials to an existing repo? (I.e., separate optimization tasks/scripts)

## 9. sparks-baird/mat_discover (2022-12-29, 351 words)

<https://github.com/sparks-baird/mat_discover/discussions/134#discussioncomment-4552235>

> Taking from a Theory of Predictive Modeling course I took at BYU, a learning problem has the following three aspects:
> 
> Data
> A "bucket of models" to choose from (i.e., model(s) and their hyperparameters)
> A "notion of best" (measuring stick)
> 
> If the question is about hyperparameter tuning for unsupervised tasks, then the data and bucket of models are likely well-defined, but the notion of best isn't. RMSE and MAE are straightforward "notions of best" for property prediction. However, mat-discover is a project without an obvious notion of best because the goal is to find high-performing, chemically novel materials. High performance is usually straightforward, but novelty can be pretty subjective. Some metrics I came up with were:
> 
> At each iteration, how many new periodic elements are being explored?
> At each iteration, how many new unique chemical formula templates (e.g., $\mathrm{SiO}_2$ is of the form $\mathrm{AB}_2$) are being explored? (figures)
> 
> Note that I wasn't explicitly optimizing for these - I was using these metrics to persuade myself/others that it was or wasn't carrying out novel exploration. My choice of embedding and clustering parameters was primarily based on trial and error and intuition. It was probably arbitrary at times (i.e., choose something, since a choice had to be made).
> When I presented these ideas, I received suggestions about other methods to compare with and additional metrics to try.
> There was also some great discussion and feedback about assessing the performance of an adaptive design scheme at #44.
> In the self-driving-lab-demo project, I was trying to make a case for using more sophisticated multi-objective optimization algorithms: in particular, using expected hypervolume improvement instead of scalarized objectives. See facebook/Ax#1210. My takeaway was that algorithms tend to give you what you ask for - if you ask it to minimize RMSE, it tends to give you minimal RMSE values. If you ask it to optimize the expected hypervolume improvement, it tends to give you results with improved Pareto front hypervolumes. It's up to the user to decide what fits the project's high-level goals and vision and consider the importance/cost trade-offs of performing analysis to back up the decision.

## 10. scikit-learn/scikit-learn (2022-02-05, 65 words)

<https://github.com/scikit-learn/scikit-learn/discussions/22386>

> Maybe this is relevant?
> 
>   
>     
>       scikit-learn/sklearn/neighbors/_lof.py
>     
>     
>          Line 464
>       in
>       7e1e6d0
>     
>   
>   
>     
> 
>         
>           
>            X_lrd = self._local_reachability_density(distances_X, neighbors_indices_X) 
>         
>     
>   
> 
> 
> This is inside the fit method. It wasn't clear to me how I'd get it for both the fit and the predict data. The idea is to use it in an adaptive design algorithm that progressively favors performance over novelty; however, that doesn't work if LOC rescales things every time. Any suggestions?

## 11. sparks-baird/mat_discover (2022-02-07, 138 words)

<https://github.com/sparks-baird/mat_discover/discussions/44#discussioncomment-2128164>

> think you bring up a great point about composition-only design. One other topic is the materials design of alloys; the options are kind of limited when it comes to composition (i.e. the featurization stays the same, which is good for the transferability of models but bad because the algorithm doesn't have that info about it being an alloy, fractional prevalence of phases, etc.). With the right characterization (or assumptions), I think there are some really interesting paths that could be taken with structural models in alloy design spaces.
> 
> I argue the success are due to the fact we are not exploring large enough space beyond known materials.
> 
> Could you clarify this? Success of composition-based models (or did you mean lack of success)? Not large enough meaning mostly living in "Materials Project space"? (which is a great space, granted)

## 12. micropython/micropython (2022-11-22, 76 words)

<https://github.com/orgs/micropython/discussions/10048>

> I'm having trouble finding an asymmetric public-private key system (e.g. RSA) implemented in MicroPython that's compatible with RPi Pico or Pico W and can achieve the functionality of python-rsa per the docs:
> import rsa
> (bob_pub, bob_priv) = rsa.newkeys(512)
> message = 'hello Bob!'.encode('utf8')
> crypto = rsa.encrypt(message, bob_pub)
> import rsa
> message = rsa.decrypt(crypto, bob_priv)
> print(message.decode('utf8'))
> Also, I wasn't able to get micropython-rsa-signing working. It seems to lack the required functionality described above artem-smotrakov/micropython-rsa-signing#2
> Aside: Micropython's cryptolib is symmetric.

