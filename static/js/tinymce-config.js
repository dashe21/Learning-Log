/**
 * TinyMCE Rich Text Editor Configuration for Learning Log
 */

// Initialize TinyMCE when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeTinyMCE();
    
    // Listen for theme change events instead of duplicating the listener
    document.addEventListener('themeChanged', function() {
        setTimeout(() => {
            reinitializeTinyMCE();
        }, 300); // Wait for theme transition
    });
});

function initializeTinyMCE() {
    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    
    tinymce.init({
        selector: '.rich-text-editor',
        height: 400,
        
        // Theme and skin
        skin: isDark ? 'oxide-dark' : 'oxide',
        content_css: isDark ? 'dark' : 'default',
        
        // Plugins for rich functionality
        plugins: [
            'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
            'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
            'insertdatetime', 'media', 'table', 'help', 'wordcount', 'codesample'
        ],
        
        // Toolbar configuration
        toolbar: 'undo redo | blocks | ' +
                'bold italic underline strikethrough | alignleft aligncenter ' +
                'alignright alignjustify | bullist numlist outdent indent | ' +
                'removeformat | link image | codesample | preview code | help',
        
        // Content styling
        content_style: `
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                font-size: 14px; 
                line-height: 1.6;
                color: ${isDark ? '#ffffff' : '#212529'};
                background-color: ${isDark ? '#343a40' : '#ffffff'};
            }
            .code-block {
                background-color: ${isDark ? '#495057' : '#f8f9fa'};
                border: 1px solid ${isDark ? '#6c757d' : '#dee2e6'};
                border-radius: 4px;
                padding: 12px;
                font-family: 'Courier New', monospace;
                margin: 8px 0;
            }
            blockquote {
                border-left: 4px solid #0d6efd;
                margin: 16px 0;
                padding: 8px 16px;
                background-color: ${isDark ? '#495057' : '#f8f9fa'};
            }
        `,
        
        // Learning-focused formats
        block_formats: 'Paragraph=p; Heading 1=h1; Heading 2=h2; Heading 3=h3; Heading 4=h4; Preformatted=pre; Blockquote=blockquote',
        
        // Image upload configuration
        automatic_uploads: false,
        file_picker_types: 'image',
        
        // Learning Log specific settings
        elementpath: false,
        branding: false,
        resize: true,
        menubar: false,
        
        // Mobile responsive configuration
        mobile: {
            theme: 'silver', // Use modern silver theme instead of limited mobile theme
            plugins: ['autosave', 'lists', 'autolink', 'link'],
            toolbar: 'undo redo | bold italic | bullist numlist | link',
            menubar: false,
            toolbar_mode: 'wrap' // Allow toolbar to wrap on small screens
        },
        
        // Custom setup
        setup: function(editor) {
            editor.on('init', function() {
                // Add essential custom styles
                addCustomStyles(editor, isDark);
                
                // Simple toolbar overflow handling
                setupToolbarDismiss(editor);
                
                // Setup form validation handling
                setupFormValidation(editor);
            });
            
            // Auto-save functionality
            editor.on('input', function() {
                localStorage.setItem('tinymce_draft_' + editor.id, editor.getContent());
            });
            
            // Clear draft on form submission
            editor.on('submit', function() {
                localStorage.removeItem('tinymce_draft_' + editor.id);
            });
            
            // Sync content before form submission
            editor.on('BeforeSubmit', function() {
                editor.save();
            });
        },
        
        // Restore drafts
        init_instance_callback: function(editor) {
            const draft = localStorage.getItem('tinymce_draft_' + editor.id);
            if (draft && !editor.getContent()) {
                editor.setContent(draft);
            }
        }
    });
}

function reinitializeTinyMCE() {
    if (typeof tinymce !== 'undefined') {
        tinymce.remove('.rich-text-editor');
        initializeTinyMCE();
    }
}

function addCustomStyles(editor, isDark) {
    // Keep only essential code block styling that's actually used
    const customCSS = `
        .code-block {
            background-color: ${isDark ? '#495057' : '#f8f9fa'};
            border: 1px solid ${isDark ? '#6c757d' : '#dee2e6'};
            border-radius: 4px;
            padding: 12px;
            font-family: 'Courier New', monospace;
            margin: 8px 0;
        }
    `;
    
    const style = editor.dom.create('style', {type: 'text/css'}, customCSS);
    editor.getDoc().getElementsByTagName('head')[0].appendChild(style);
}

function setupToolbarDismiss(editor) {
    // Simple toolbar overflow handling - TinyMCE handles most of this automatically
    editor.on('keydown', function(e) {
        // Close overflow menu with ESC key
        if (e.keyCode === 27) { // ESC key
            const editorContainer = editor.getContainer();
            const overflowButton = editorContainer?.querySelector('.tox-toolbar__overflow-button');
            
            if (overflowButton && overflowButton.getAttribute('aria-pressed') === 'true') {
                overflowButton.click(); // Toggle closed
            }
        }
    });
}

function setupFormValidation(editor) {
    // Find the form containing this editor
    const form = editor.getElement().closest('form');
    if (!form) return;
    
    // Override form submission to ensure TinyMCE content is validated
    form.addEventListener('submit', function(e) {
        // Sync TinyMCE content to textarea
        editor.save();
        
        // Get the content
        const content = editor.getContent();
        
        // Basic validation (matches server-side validation)
        if (!content || content.trim() === '' || content.replace(/<[^>]*>/g, '').trim().length < 10) {
            e.preventDefault();
            
            // Show validation error
            showValidationError(editor, 'Content must be at least 10 characters long.');
            
            // Focus the editor
            editor.focus();
            
            return false;
        }
        
        // Clear any existing validation errors
        clearValidationError(editor);
        
        return true;
    });
}

function showValidationError(editor, message) {
    const container = editor.getContainer();
    
    // Add invalid class to editor container
    container.classList.add('tox-tinymce-invalid');
    
    // Find or create error message element
    let errorElement = container.nextElementSibling;
    if (!errorElement || !errorElement.classList.contains('tinymce-validation-error')) {
        errorElement = document.createElement('div');
        errorElement.classList.add('tinymce-validation-error', 'invalid-feedback', 'd-block');
        container.parentNode.insertBefore(errorElement, container.nextSibling);
    }
    
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

function clearValidationError(editor) {
    const container = editor.getContainer();
    
    // Remove invalid class
    container.classList.remove('tox-tinymce-invalid');
    
    // Hide error message
    const errorElement = container.nextElementSibling;
    if (errorElement && errorElement.classList.contains('tinymce-validation-error')) {
        errorElement.style.display = 'none';
    }
}