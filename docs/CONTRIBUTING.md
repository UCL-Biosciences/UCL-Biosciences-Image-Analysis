# Contributing
A few notes aimed at anyone who wants to contrute to the repo. It would be great for this to be supported by the community.

So please get in touch if you have any:
- suggestions for improving current material
- requests for what could be added
- your own material that you think would make a good contribution

## Some important tips
- Clone the repository and make the conda environments first.
- We will organise tasks in the Issues tab. Share updates and questions there. Assign tasks to yourself if you are working on something.
- Make a new branch for any work you are doing. Be careful to branch _from_ the branch you want to work on.
- Keep branches focussed and try to only edit code relevant to the aim of the branch.
- Make your changes, check it all runs, push back to the dedicated branch on the repo, and open a Pull Request to merge with the relevant branch.
- Pull regularly to stay up to date
- Write clear messages so everyone can see what changes you've made

## Branch structure
`main` is the main branch. We should not use this to add new material. Once up and running, do all development, testing, new features on seperate branches. With the caveat that we are doing a lot of commits to main as we tidy up notebooks and docs in May 2026!

The `hpc-scripting` branch contains work-in-progress toward a scripting workflow for HPC job submission. The idea was that functions and configs used in the notebooks could also feed into a job array script, allowing users to refine parameters interactively in a notebook before submitting batch jobs to process large image datasets in parallel. This work is parked for now but preserved on that branch to pick up later.
