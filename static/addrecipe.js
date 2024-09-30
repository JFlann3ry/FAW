document.addEventListener('DOMContentLoaded', function() {
    // Increment the step count when adding a new step dynamically
    document.getElementById('add_step').addEventListener('click', function() {
        var instructionsDiv = document.getElementById('steps');
        var currentCount = instructionsDiv.getElementsByClassName('steps').length;
        var newInstructionTextarea = document.createElement('textarea');
        newInstructionTextarea.classList.add('steps');
        newInstructionTextarea.name = 'step[]';  // Use array notation for dynamic steps
        newInstructionTextarea.maxLength = 256;
        newInstructionTextarea.rows = 4;
        newInstructionTextarea.cols = 50;
        newInstructionTextarea.placeholder = 'Step ' + (currentCount + 1);
        instructionsDiv.appendChild(newInstructionTextarea);
        instructionsDiv.appendChild(document.createElement('br'));

        // Increment the step count value
        document.getElementById('step_count').value = currentCount + 1;
    });

    // Add event listener to the "Add Ingredient" button
    document.getElementById('add_ingredient').addEventListener('click', function() {
        // Create ingredient container div
        var ingredientContainer = document.createElement('div');
        
        // Ingredient Name input
        var ingredientNameInput = document.createElement('input');
        ingredientNameInput.type = 'text';
        ingredientNameInput.name = 'ingredient_name[]'; // Use array notation for dynamic ingredients
        ingredientNameInput.placeholder = 'Ingredient Name';
        ingredientContainer.appendChild(ingredientNameInput);

        // Instruction input
        var instructionInput = document.createElement('input');
        instructionInput.type = 'text';
        instructionInput.name = 'instruction[]'; // Use array notation for dynamic instructions
        instructionInput.placeholder = 'Instruction';
        ingredientContainer.appendChild(instructionInput);

        // Quantity input
        var quantityInput = document.createElement('input');
        quantityInput.type = 'text';
        quantityInput.name = 'quantity[]'; // Use array notation for dynamic quantities
        quantityInput.placeholder = 'Quantity';
        ingredientContainer.appendChild(quantityInput);

        // Unit input
        var unitInput = document.createElement('input');
        unitInput.type = 'text';
        unitInput.name = 'unit[]'; // Use array notation for dynamic units
        unitInput.placeholder = 'Unit';
        ingredientContainer.appendChild(unitInput);

        // Category input
        var categoryInput = document.createElement('input');
        categoryInput.type = 'text';
        categoryInput.name = 'category[]'; // Use array notation for dynamic categories
        categoryInput.placeholder = 'Category';
        ingredientContainer.appendChild(categoryInput);

        // Append ingredient container to the ingredients section
        document.getElementById('ingredients').appendChild(ingredientContainer);
    });

// Function to reload tags from the server and update the UI
function reloadTags() {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", "/fetch-tags", true); // Assuming you have a route to fetch tags
    xhr.onload = function() {
        if (xhr.status === 200) {
            // Update the tag list in the UI
            const tagSection = document.getElementById("tag-section");
            tagSection.innerHTML = xhr.responseText;
        } else {
            console.error("Error reloading tags:", xhr.statusText);
        }
    };
    xhr.onerror = function() {
        console.error("Network error occurred");
    };
    xhr.send();
}

// Add event listener to the "Add Tag" button
const addTagButton = document.getElementById("add_tag_button");
addTagButton.addEventListener("click", function() {
    const newTagName = document.getElementById("new_tag").value.trim();
    if (newTagName !== "") {
        // Perform AJAX request to add new tag
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/add_tag", true);
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhr.onload = function() {
            if (xhr.status === 200) {
                // Reload tags from the server
                reloadTags();
            } else {
                // Handle error
                console.error("Error adding tag:", xhr.statusText);
            }
        };
        xhr.onerror = function() {
            console.error("Network error occurred");
        };
        xhr.send("tag_name=" + encodeURIComponent(newTagName));
    } else {
        // Empty tag name, display error or do nothing
    }
});


});
