// JavaScript (editrecipe.js)
$(document).ready(function() {
    // Add ingredient
    $('#add-ingredient').click(function() {
        var newIngredient = `
            <div class="ingredient">
                <input type="text" name="ingredient_name[]" placeholder="Ingredient Name">
                <input type="text" name="instruction[]" placeholder="Instruction">
                <input type="text" name="quantity[]" placeholder="Quantity">
                <input type="text" name="unit[]" placeholder="Unit">
                <input type="text" name="category[]" placeholder="Category">
                <button type="button" class="remove-ingredient">Remove</button><br>
            </div>
        `;
        $('#ingredient-container').append(newIngredient);
    });

    // Remove ingredient
    $('#ingredient-container').on('click', '.remove-ingredient', function() {
        $(this).parent().remove();
    });

    // Add step
    $('#add-step').click(function() {
        var newStep = `
            <div>
                <textarea name="step[]" maxlength="256" rows="4" cols="50" placeholder="Step"></textarea>
                <button type="button" class="remove-step">Remove</button><br>
            </div>
        `;
        $('#step-container').append(newStep);
    });

    // Remove step
    $('#step-container').on('click', '.remove-step', function() {
        $(this).parent().remove();
    });
});
