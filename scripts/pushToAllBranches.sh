git push origin develop
git checkout stage
git merge develop
git push origin stage
git checkout master
git merge stage
git push origin master