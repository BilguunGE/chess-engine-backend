# chess-engine-backend

install virtualenv for python
```
pip install virtualenv
```

go to project directory and activate the virtual env with (Mac):
```
source venv/bin/activate
```
Windows:
```
venv\Scripts\activate.bat
```
run flask in the (venv) terminal:
```
export FLASK_APP=server
export FLASK_ENV=development
flask run
```

## Working with git

First make sure that `main` is up to date.

```
git pull origin main
```

Create a new branch from main and switch to that branch:

```
git checkout -b "name-of-your-branch"
```

Here you can do your changes. Please use kebab-case (this-is-kebab-case) for the branch name.

If you're done stage your changes:

```
git add .
```

Then commit them with a message:

```
git commit -m "Changed navigation bar"
```

Make sure you're branch is still up to date with `main`:

```
git pull origin main
```

and solve merge conflicts if there are any.

Finally make a Pull Request by pushing to the remote repo:

```
git push origin name-of-your-branch
```

Now your branch is also on the remote repo.
You can go back to `main` and also delete your branch if it was merged to `main`.
To checkout `main` or any other branch:

```
git checkout main
```

To delete a branch after it was merged and is not needed anymore:

```
git branch -D name-of-your-branch
```

Some more useful git commands:

-   `git checkout -b branch-name` to create a new branch on your local repo and check it out immediately.
-   `git stash` or `git stash save name-of-wip-changes` to save uncommitted changes. Quite handy if you worked on a different branch and want to move your changes to another branch. But doesn't save untracked files.
-   `git stash pop` to pop the last stashed changes
-   `git stash pop name-of-wip-changes` to pop some specific changes saved in your stash
-   `git cherry-pick commitnumberlookinglikethis271676271bsgasjgt92791shgh` to move a commit from any branch to your current position
-   `git branch -m new-name-of-branch` to rename the current branch
