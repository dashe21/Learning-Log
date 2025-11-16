/**
 * Tag Input Widget for Learning Log
 * Provides autocomplete and tag management functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeTagInputs();
});

function initializeTagInputs() {
    const tagInputs = document.querySelectorAll('.tag-input');
    
    tagInputs.forEach(function(input) {
        setupTagInput(input);
    });
}

function setupTagInput(input) {
    // Create container for tags and new input
    const container = document.createElement('div');
    container.className = 'tag-input-container';
    
    // Create tags display area
    const tagsContainer = document.createElement('div');
    tagsContainer.className = 'tags-display d-flex flex-wrap align-items-center border rounded p-2';
    tagsContainer.style.minHeight = '42px';
    tagsContainer.style.cursor = 'text';
    
    // Create new tag input
    const newTagInput = document.createElement('input');
    newTagInput.type = 'text';
    newTagInput.className = 'new-tag-input border-0 flex-grow-1';
    newTagInput.style.outline = 'none';
    newTagInput.style.minWidth = '120px';
    newTagInput.placeholder = input.placeholder || 'Type tag name...';
    
    // Hide original input
    input.style.display = 'none';
    
    // Insert container after original input
    input.parentNode.insertBefore(container, input.nextSibling);
    container.appendChild(tagsContainer);
    tagsContainer.appendChild(newTagInput);
    
    // Initialize with existing tags
    const existingTags = input.value ? input.value.split(',').map(tag => tag.trim()).filter(tag => tag) : [];
    existingTags.forEach(tagName => addTag(tagsContainer, newTagInput, input, tagName));
    
    // Auto-complete functionality
    setupAutocompleteInline(newTagInput, tagsContainer, input);
}

function addTag(container, newTagInput, originalInput, tagName) {
    const tag = document.createElement('span');
    tag.className = 'tag-item badge bg-primary me-1 mb-1';
    tag.style.cursor = 'pointer';
    tag.innerHTML = `
        ${tagName}
        <i class="bi bi-x ms-1" style="cursor: pointer;"></i>
    `;
    
    // Add remove functionality
    tag.querySelector('.bi-x').addEventListener('click', function() {
        removeTag(tag, originalInput);
    });
    
    // Insert before the input
    container.insertBefore(tag, newTagInput);
    
    // Update original input value
    updateOriginalInput(originalInput);
}

function removeTag(tagElement, originalInput) {
    tagElement.remove();
    updateOriginalInput(originalInput);
}

function hasTag(container, tagName) {
    const tags = container.querySelectorAll('.tag-item');
    return Array.from(tags).some(tag => tag.textContent.trim() === tagName);
}

function updateOriginalInput(originalInput) {
    const container = originalInput.nextSibling;
    const tags = container.querySelectorAll('.tag-item');
    const tagNames = Array.from(tags).map(tag => tag.textContent.trim());
    originalInput.value = tagNames.join(',');
}

    function setupAutocompleteInline(newTagInput, tagsContainer, input) {
        // Autocomplete state
        let autocompleteContainer = null;
        let currentSuggestions = [];
        
        // Hide suggestions function
        function hideSuggestions() {
            if (autocompleteContainer) {
                autocompleteContainer.remove();
                autocompleteContainer = null;
            }
            currentSuggestions = [];
        }
        
        newTagInput.addEventListener('input', function() {
            const query = newTagInput.value.trim();
            
            if (query.length >= 2) {
                // Fetch suggestions from API
                fetch(`/api/tags/search?q=${encodeURIComponent(query)}&limit=8`)
                    .then(response => {
                        return response.json();
                    })
                    .then(suggestions => {
                        showSuggestions(suggestions.filter(suggestion => 
                            !hasTag(tagsContainer, suggestion.name)
                        ));
                    })
                    .catch((error) => {
                        console.error('Error fetching suggestions:', error);
                        // Hide suggestions on error
                        hideSuggestions();
                    });
            } else {
                hideSuggestions();
            }
        });
        
        // Main keydown event listener for tag input
        newTagInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                
                // Check if there's a selected suggestion
                if (autocompleteContainer && autocompleteContainer.querySelector('.bg-light')) {
                    const selectedItem = autocompleteContainer.querySelector('.bg-light');
                    const suggestionName = selectedItem.querySelector('.badge').textContent.trim();
                    addTag(tagsContainer, newTagInput, input, suggestionName);
                    newTagInput.value = '';
                    hideSuggestions();
                } else {
                    // Add the typed tag
                    const tagName = newTagInput.value.trim();
                    if (tagName && !hasTag(tagsContainer, tagName)) {
                        addTag(tagsContainer, newTagInput, input, tagName);
                        newTagInput.value = '';
                        hideSuggestions();
                    }
                }
            } else if (e.key === 'Backspace' && newTagInput.value === '') {
                // Remove last tag if input is empty
                const tags = tagsContainer.querySelectorAll('.tag-item');
                if (tags.length > 0) {
                    removeTag(tags[tags.length - 1], input);
                }
            } else if (e.key === 'ArrowDown' && currentSuggestions.length > 0) {
                e.preventDefault();
                selectSuggestion(0);
            } else if (e.key === 'Escape') {
                hideSuggestions();
            }
        });
        
        // Blur event listener
        newTagInput.addEventListener('blur', function() {
            // Small delay to allow click on suggestion to register first
            setTimeout(() => {
                if (!autocompleteContainer) { // Only add if suggestions are not open
                    const tagName = newTagInput.value.trim();
                    if (tagName && !hasTag(tagsContainer, tagName)) {
                        addTag(tagsContainer, newTagInput, input, tagName);
                        newTagInput.value = '';
                    }
                }
            }, 150);
        });
        
        // Focus on container click
        tagsContainer.addEventListener('click', function() {
            newTagInput.focus();
        });
        
        function showSuggestions(suggestions) {
            hideSuggestions();
            
            if (suggestions.length === 0) return;
            
            currentSuggestions = suggestions;
            autocompleteContainer = document.createElement('div');
            autocompleteContainer.className = 'tag-autocomplete position-absolute border rounded shadow-sm';
            autocompleteContainer.style.zIndex = '1000';
            autocompleteContainer.style.minWidth = '200px';
            autocompleteContainer.style.maxHeight = '200px';
            autocompleteContainer.style.overflowY = 'auto';
            
            suggestions.forEach((suggestion, index) => {
                const item = document.createElement('div');
                item.className = 'suggestion-item px-3 py-2 cursor-pointer';
                item.style.cursor = 'pointer';
                item.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="badge me-2" style="background-color: ${suggestion.color}; color: white;">
                            ${suggestion.name}
                        </span>
                        <small class="text-muted">${suggestion.usage_count} uses</small>
                    </div>
                    ${suggestion.category ? `<small class="text-muted">${suggestion.category}</small>` : ''}
                `;
                
                item.addEventListener('mouseenter', function() {
                    selectSuggestion(index);
                });
                
                item.addEventListener('mousedown', function(e) {
                    // Prevent blur event from firing before click
                    e.preventDefault();
                });
                
                item.addEventListener('click', function() {
                    addTag(tagsContainer, newTagInput, input, suggestion.name);
                    newTagInput.value = '';
                    hideSuggestions();
                    newTagInput.focus(); // Refocus after adding tag
                });
                
                autocompleteContainer.appendChild(item);
            });
            
            // Position the autocomplete
            const rect = newTagInput.getBoundingClientRect();
            autocompleteContainer.style.top = (rect.bottom + window.scrollY) + 'px';
            autocompleteContainer.style.left = rect.left + 'px';
            
            document.body.appendChild(autocompleteContainer);
        }
        
        function selectSuggestion(index) {
            if (!autocompleteContainer) return;
            
            // Remove previous selection
            const items = autocompleteContainer.querySelectorAll('.suggestion-item');
            items.forEach(item => item.classList.remove('bg-light'));
            
            // Add selection to current item
            if (items[index]) {
                items[index].classList.add('bg-light');
            }
        }
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!tagsContainer.contains(e.target) && !autocompleteContainer?.contains(e.target)) {
                hideSuggestions();
            }
        });
    }