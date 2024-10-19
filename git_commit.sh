read -p "Enter branch name: " BRANCH
read -p "Enter commit message: " COMMIT

if git show-ref --verify --quiet refs/heads/$BRANCH; then
    git checkout $BRANCH
else
    git checkout -b $BRANCH
fi
git add .
git commit -m "$COMMIT"
git push origin $BRANCH
git fetch origin
git merge origin/main

if [ $? -ne 0 ]; then
    echo "There are conflicts with main."
else
    echo "No conflicts with main."
    read -p "Do you want to merge to main? (y/n): " MERGE_TO_MAIN

    if [ "$MERGE_TO_MAIN" = "y" ]; then
        git checkout main
        git merge $BRANCH
        git push origin main
    else
        echo "Merge to main aborted."
    fi
fi
