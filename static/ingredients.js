function addIngredient() {
    var ingredient = document.getElementById("ingredient").value;
    var instructions = document.getElementById("instructions").value;
    var quantity = document.getElementById("quantity").value;
    var unit = document.getElementById("unit").value;
    var category = document.getElementById("category").value;
  
    // Create a new table row
    var newRow = document.createElement("tr");
    // Populate the row with ingredient data
    newRow.innerHTML = "<td>" + ingredient + "</td><td>" + instructions + "</td><td>" + quantity + "</td><td>" + unit + "</td><td>" + category + "</td>";
  
    // Append the new row to the table body
    document.getElementById("ingredientBody").appendChild(newRow);
  
    // Clear input fields after adding ingredient
    document.getElementById("ingredient").value = "";
    document.getElementById("instructions").value = "";
    document.getElementById("quantity").value = "";
    document.getElementById("unit").value = "";
    document.getElementById("category").value = "";
  
    // Prevent form submission (if the button is inside a form)
    return false;
}

function deleteIngredient(ingredientId) {
    fetch("/delete_ingredient", {
        method: "POST",
        body: JSON.stringify({ ingredientId: ingredientId }),
        headers: {
            "Content-Type": "application/json"
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the ingredient row from the table
            document.getElementById("ingredientBody").querySelector(`[data-id="${ingredientId}"]`).remove();
            flashMessage("Ingredient deleted successfully!", "success");
        } else {
            flashMessage("Failed to delete ingredient.", "error");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        flashMessage("An error occurred while deleting the ingredient.", "error");
    });
}

function flashMessage(message, messageType) {
    // Flash a message using Flask's flash functionality
    fetch("/flash_message", {
        method: "POST",
        body: JSON.stringify({ message: message, messageType: messageType }),
        headers: {
            "Content-Type": "application/json"
        }
    });
}
