<!-- cringe-lint: disable-file -->
# Exemplars: tutorial-adjacent

Real human-written passages, selected because their surface
statistics sit near the median for this register. Showing these
works better than describing them: in a 100-author study, directed
linguistic guidance generally performed worse than plain exemplar
prompting, and 300-word exemplars beat 50-word ones.

12 passages, 1416 words. All from public repositories.

## 1. AccelerationConsortium/ac-microcourses (2025-04-18, 95 words)

<https://github.com/AccelerationConsortium/ac-microcourses/discussions/159#discussioncomment-12873809>

> Im wondering if the insert.py is reflecting the newest version. In particular, pymongo can't be used within MicroPython. Can you commit your latest files and include a link to your assignment repo here so I can check?
> I haven't seen this error before, but it may be related to storage space on your microcontroller. Could you try deleting all files on it (except maybe your HiveMQ certificate so you don't have to regenerate it) and reuploading the necessary ones for module 5?
> If that doesn't work, could you also try reflashing MicroPython onto the microcontroller?

## 2. anthony-wang/CrabNet (2022-01-07, 114 words)

<https://github.com/anthony-wang/CrabNet/issues/10#issuecomment-1007145550>

> , looks like MODNet implemented multi-class classification. Sounds like they just replaced a softmax activation function with a sigmoid. See   In particular, see the changes in  . They use   and   instead of  , and pass in something to   as shown here. I'd have to dig a bit deeper (in reality, shallower in terms of MODNet's stack trace) to see how they use the sigmoid, but I imagine that for 20 possible labels, they just divide the sigmoid into 20 equal segments and find which bin it fits into. Let me know if you need help with this. If you open up an issue with MODNet asking about it, they would probably help out, too.

## 3. anthony-wang/CrabNet (2022-01-07, 114 words)

<https://github.com/anthony-wang/CrabNet/issues/10#issuecomment-1007145550>

> , looks like MODNet implemented multi-class classification. Sounds like they just replaced a softmax activation function with a sigmoid. See   In particular, see the changes in  . They use   and   instead of  , and pass in something to   as shown here. I'd have to dig a bit deeper (in reality, shallower in terms of MODNet's stack trace) to see how they use the sigmoid, but I imagine that for 20 possible labels, they just divide the sigmoid into 20 equal segments and find which bin it fits into. Let me know if you need help with this. If you open up an issue with MODNet asking about it, they would probably help out, too.

## 4. sparks-baird/self-driving-lab-demo (2022-10-29, 149 words)

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

## 5. sparks-baird/self-driving-lab-demo (2022-08-13, 307 words)

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

## 6. AccelerationConsortium/ac-microcourses (2024-09-17, 84 words)

<https://github.com/AccelerationConsortium/ac-microcourses/pull/52#discussion_r1764065582>

> This video seems pretty reasonable. While I didn't watch it in full, it looks fairly recent and has a decent number of views and likes. It would be best for possible for at least one of us to watch a video in full before linking out to it. In general it's best to find videos that are from an official source, but I don't think there would be for this one. That may often be the case. Sometimes the non-official videos are better too.

## 7. sparks-baird/mat_discover (2022-02-25, 54 words)

<https://github.com/sparks-baird/mat_discover/issues/56#issuecomment-1051126333>

> One thing that might be happening is it's not looking in the right channels (though normally I would expect conda to let you know when a package isn't found). One thing you can try is to add the   and   channels to your miniconda settings explicitly before installing. At that point, the   flag is moot.

## 8. sparks-baird/matbench-genmetrics (2022-07-29, 164 words)

<https://github.com/sparks-baird/matbench-genmetrics/issues/9#issuecomment-1199809707>

> ### from internal discussion, by  
>  
>  
>  
>  
>  
>  
>  
>  
>  
>  
> 
> ### Comments
> 
> #### StructureMatcher
>  
> 
> For generative models, especially when symmetry isn't directly imposed, this seems like an important feature. Related:   Forcing models to respect a given symmetry seems like a better route but a lot less straightforward. I don't think even CDVAE, which I consider state-of-the-art for crystal generative models, enforces symmetry explicitly.
>  
> 
> Is the main issue here that it's computationally expensive?
>  
> 
> 
> Is the idea here that we get nice groupings of structures similar to how we can request all chemical formulas from a given chemical system? Is there any benefit in terms of speed-up or is the main benefit provenance and consistency?
>  
> 
> For the current implementation of  , we take a train/test split and a set of generated structures, and compare train vs. generated (novelty), test vs. generated (coverage), and generated vs. generated (uniqueness).
> 
> #### XtalFinder
>  
> 
> This is really good to know. I don't think I would have caught that nuance immediately. Kind of goes back to  's

## 9. sparks-baird/mat_discover (2022-03-10, 70 words)

<https://github.com/sparks-baird/mat_discover/issues/39#issuecomment-1063666986>

> Since changing over to   instead of  , now Google Colab doesn't show any of the   figures, only the   ones, and it runs without error. It seems to save all the appropriate files in the side panel under  , but the   files need to be downloaded and opened separately.
> 
> Related:  
> 
>   I'm wondering if this error has to do with having too few clusters or if it really is a package compatibility.

## 10. sgbaird/honegumi (2023-06-28, 60 words)

<https://github.com/sgbaird/honegumi/discussions/2#discussioncomment-6301573>

> Exposing as a PyScaffold extension
> Perhaps as a separate package.
> 
> put the notebooks into the notebooks folder, unit test(s) associated with that notebook into the tests folder, tables into the data folder (if applicable), make a copy of dependencies (loose and strict), etc.
> Should there be an option to add new tutorials to an existing repo? (I.e., separate optimization tasks/scripts)

## 11. sparks-baird/xtal2png (2022-07-09, 146 words)

<https://github.com/sparks-baird/xtal2png/issues/50#issuecomment-1179464817>

> It does leave the question on my mind, why does the regression results are so poor (much worse than dummy), whereas the classification results are OK (a bit better than dummy). 
> 
> A follow-up computational experiment (that I think we should leave on the back-burner until further notice) is using the classification model, but with bins for the classes (e.g. formation energy between 0 and 0.05). Implementing ordinal classification would be extra work, so first treat it as categorical. I'm putting this here more as a future reference sort of thing as things progress with  . 
> 
> It's also interesting in the sense that hyperparameter-tuned XGBoost did a pretty good job on the regression task (~4x better than the CNN regression), and this was with much less information. We'll see if the results still hold when we double-check that data leakage wasn't coming into play. #51 and specifically

## 12. sparks-baird/CrabNet (2023-08-28, 59 words)

<https://github.com/sparks-baird/CrabNet/issues/71#issuecomment-1696080483>

> Hi, can you provide a minimal working example? My guess is that there's something non-standard in how one (or multiple) of your formulas is represented. Try this with a subset of formulas and provide the results and which formulas were used in the subset.
> 
> For example, I think you could use the following dummy data (taken from mat-discover docs):

