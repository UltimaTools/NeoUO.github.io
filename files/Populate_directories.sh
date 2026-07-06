#!/bin/bash

# Find all subdirectories containing a file named ".Resource"
for resource_file in */.Resource; do
    # Extract the directory name (category directory)
    DIR="${resource_file%/.Resource}"
    
    # Create a user-friendly category name by capitalizing the directory name
    # Replace underscores with spaces and capitalize each word
    NAME=$(echo "$DIR" | sed -E 's/_/ /g; s/(^| )(.)/\U\2/g')

    # Print the directory being processed
    echo "Generating index.html for directory: $DIR (Category Name: $NAME)"

    # Create the 'files' directory under DIR
    mkdir -p "$DIR/files"

    # Generate the index.html using sed
    sed -e "s#CATEGORY_NAME#$NAME#g" \
        -e "s#CATEGORY_DIR#$DIR#g" \
        category_template.html > "$DIR/index.html"
done
