function showTagInput() {
    document.getElementById('add-tag-btn').style.display = 'none';
    document.getElementById('tag-input').style.display = 'block';
}

function saveTag() {
    var tagName = document.getElementById('tag-name-input').value;
    if (tagName.trim() === '') {
        alert('Tag name cannot be empty!');
        return;
    }

    // AJAX request to check if tag exists
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/check_tag', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function () {
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            if (response.exists) {
                document.getElementById('tag-name-input').value = ''; // Clear input field
                document.getElementById('add-tag-btn').style.display = 'block';
                document.getElementById('tag-input').style.display = 'none';
                alert('Tag already exists!');
            } else {
                // Tag doesn't exist, proceed to save
                // You can perform additional validation or directly save the tag here
                // For simplicity, I'll just submit the form
                document.getElementById('add-tag-form').submit();
            }
        } else {
            alert('Request failed. Please try again later.');
        }
    };
    xhr.send(JSON.stringify({tag_name: tagName}));
}

function toggleEdit() {
    var deleteButtons = document.getElementsByClassName('delete-tag-btn');
    var editTagsButton = document.getElementById('edit-tags-btn');

    // Toggle visibility of delete buttons
    for (var i = 0; i < deleteButtons.length; i++) {
        if (deleteButtons[i].style.display === 'none') {
            deleteButtons[i].style.display = 'inline-block';
        } else {
            deleteButtons[i].style.display = 'none';
        }
    }

    // Change text of Edit Tags button
    if (editTagsButton.innerHTML === 'Edit Tags') {
        editTagsButton.innerHTML = 'Done Editing';
    } else {
        editTagsButton.innerHTML = 'Edit Tags';
    }
}

function deleteTag(tagName) {
    if (confirm('Are you sure you want to delete the tag "' + tagName + '"?')) {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/delete_tag', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function () {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.success) {
                    // Reload the page to update the tag list
                    window.location.reload();
                } else {
                    alert('Failed to delete tag.');
                }
            } else {
                alert('Request failed. Please try again later.');
            }
        };
        xhr.send(JSON.stringify({tag_name: tagName}));
    }
}
