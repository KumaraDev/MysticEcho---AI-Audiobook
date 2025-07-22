/**
 * Mystic Echo Editor JavaScript
 * Handles rich text editing, auto-save, AI integration, and file operations
 */

class MysticEditor {
    constructor(projectId) {
        this.projectId = projectId;
        this.currentContent = '';
        this.lastSavedContent = '';
        this.autoSaveTimer = null;
        this.autoSaveInterval = 30000; // 30 seconds
        this.currentSuggestion = null;
        this.isInitialized = false;
        
        this.init();
    }
    
    init() {
        this.initializeEditor();
        this.setupEventListeners();
        this.startAutoSave();
        this.isInitialized = true;
        console.log('Mystic Editor initialized for project:', this.projectId);
    }
    
    initializeEditor() {
        const self = this;
        
        tinymce.init({
            selector: '#editor-content',
            height: 600,
            menubar: false,
            plugins: [
                'wordcount', 'autoresize', 'link', 'lists', 'table', 
                'code', 'paste', 'searchreplace', 'autolink'
            ],
            toolbar: [
                'undo redo | bold italic underline strikethrough | bullist numlist | link unlink',
                'table | searchreplace | code | wordcount'
            ].join(' | '),
            content_style: `
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
                    font-size: 16px; 
                    line-height: 1.6; 
                    color: #e9ecef;
                    background-color: #212529;
                    padding: 20px;
                }
                p { margin-bottom: 1em; }
                h1, h2, h3, h4, h5, h6 { 
                    margin-top: 1.5em; 
                    margin-bottom: 0.5em; 
                    font-weight: bold;
                }
            `,
            skin: 'oxide-dark',
            content_css: 'dark',
            paste_data_images: true,
            paste_as_text: true,
            browser_spellcheck: true,
            contextmenu: false,
            setup: function(editor) {
                editor.on('init', function() {
                    self.updateWordCount();
                    self.currentContent = editor.getContent();
                    self.lastSavedContent = self.currentContent;
                });
                
                editor.on('input keyup paste', function() {
                    self.updateWordCount();
                    self.scheduleAutoSave();
                });
                
                editor.on('selectionchange', function() {
                    self.updateSelectionInfo();
                });
            }
        });
    }
    
    setupEventListeners() {
        // PDF Upload
        const pdfUpload = document.getElementById('pdf-upload');
        if (pdfUpload) {
            pdfUpload.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    this.uploadPDF(file);
                }
            });
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 's':
                        e.preventDefault();
                        this.saveProject();
                        break;
                    case 'b':
                        e.preventDefault();
                        tinymce.get('editor-content').execCommand('Bold');
                        break;
                    case 'i':
                        e.preventDefault();
                        tinymce.get('editor-content').execCommand('Italic');
                        break;
                }
            }
            
            // AI shortcuts
            if (e.altKey) {
                switch(e.key) {
                    case '1':
                        e.preventDefault();
                        this.getAISuggestions('improve');
                        break;
                    case '2':
                        e.preventDefault();
                        this.getAISuggestions('expand');
                        break;
                    case '3':
                        e.preventDefault();
                        this.getAISuggestions('summarize');
                        break;
                }
            }
        });
        
        // Window beforeunload
        window.addEventListener('beforeunload', (e) => {
            if (this.hasUnsavedChanges()) {
                e.preventDefault();
                e.returnValue = '';
            }
        });
    }
    
    updateWordCount() {
        const editor = tinymce.get('editor-content');
        if (!editor) return;
        
        const content = editor.getContent({ format: 'text' });
        const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;
        const characterCount = content.length;
        
        const wordCountElement = document.getElementById('word-count');
        if (wordCountElement) {
            wordCountElement.textContent = `${wordCount} words, ${characterCount} characters`;
        }
        
        this.currentContent = editor.getContent();
        
        // Update progress indication
        this.updateProgressIndicator(wordCount);
    }
    
    updateProgressIndicator(wordCount) {
        // Typical audiobook is 70,000-90,000 words
        const targetWords = 80000;
        const progress = Math.min((wordCount / targetWords) * 100, 100);
        
        const progressElement = document.querySelector('.progress-bar');
        if (progressElement) {
            progressElement.style.width = `${progress}%`;
            progressElement.setAttribute('aria-valuenow', progress);
        }
    }
    
    updateSelectionInfo() {
        const editor = tinymce.get('editor-content');
        if (!editor) return;
        
        const selectedText = editor.selection.getContent({ format: 'text' });
        const selectionLength = selectedText.length;
        
        // Update AI button states
        const aiButtons = document.querySelectorAll('[onclick*="getAISuggestions"]');
        aiButtons.forEach(button => {
            button.disabled = selectionLength === 0;
            if (selectionLength === 0) {
                button.title = 'Select text to enable AI suggestions';
            } else {
                button.title = `Generate suggestions for ${selectionLength} characters`;
            }
        });
    }
    
    scheduleAutoSave() {
        clearTimeout(this.autoSaveTimer);
        
        const statusElement = document.getElementById('auto-save-status');
        if (statusElement) {
            statusElement.textContent = 'Unsaved changes';
            statusElement.className = 'text-warning';
        }
        
        this.autoSaveTimer = setTimeout(() => {
            if (this.hasUnsavedChanges()) {
                this.saveProject(true);
            }
        }, 5000); // Auto-save after 5 seconds of inactivity
    }
    
    startAutoSave() {
        setInterval(() => {
            if (this.hasUnsavedChanges()) {
                this.saveProject(true);
            }
        }, this.autoSaveInterval);
    }
    
    hasUnsavedChanges() {
        return this.currentContent !== this.lastSavedContent;
    }
    
    async saveProject(autoSave = false) {
        const editor = tinymce.get('editor-content');
        if (!editor) return;
        
        const content = editor.getContent();
        const saveBtn = document.getElementById('save-btn');
        const statusElement = document.getElementById('auto-save-status');
        
        if (!autoSave && saveBtn) {
            saveBtn.innerHTML = '<div class="spinner-border spinner-border-sm me-2" role="status"></div>Saving...';
            saveBtn.disabled = true;
        }
        
        try {
            const response = await fetch(`/editor/save_project/${this.projectId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content,
                    auto_save: autoSave
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.lastSavedContent = content;
                
                if (statusElement) {
                    const status = autoSave ? 'Auto-saved' : 'Saved';
                    const timestamp = new Date().toLocaleTimeString();
                    statusElement.textContent = `${status} at ${timestamp}`;
                    statusElement.className = 'text-success';
                }
                
                if (!autoSave) {
                    this.showNotification('Project saved successfully!', 'success');
                }
                
                // Update word count display
                if (data.word_count !== undefined) {
                    const wordCountElement = document.getElementById('word-count');
                    if (wordCountElement) {
                        wordCountElement.textContent = `${data.word_count} words`;
                    }
                }
            } else {
                this.showNotification(data.error || 'Failed to save project', 'error');
            }
        } catch (error) {
            console.error('Save error:', error);
            this.showNotification('Error saving project', 'error');
        } finally {
            if (!autoSave && saveBtn) {
                saveBtn.innerHTML = '<i data-feather="save" class="me-1"></i>Save';
                saveBtn.disabled = false;
                feather.replace();
            }
        }
    }
    
    async getAISuggestions(type) {
        const editor = tinymce.get('editor-content');
        if (!editor) return;
        
        const selectedText = editor.selection.getContent({ format: 'text' });
        
        if (!selectedText.trim()) {
            this.showNotification('Please select some text first', 'warning');
            return;
        }
        
        // Show loading state
        const button = document.querySelector(`[onclick*="${type}"]`);
        const originalText = button ? button.innerHTML : '';
        
        if (button) {
            button.innerHTML = '<div class="spinner-border spinner-border-sm me-1" role="status"></div>AI Working...';
            button.disabled = true;
        }
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('aiSuggestionsModal'));
        modal.show();
        
        try {
            const response = await fetch(`/editor/ai_suggestions/${this.projectId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: selectedText,
                    type: type
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.displayAISuggestions(data.suggestions, selectedText);
            } else {
                document.getElementById('ai-modal-content').innerHTML = `
                    <div class="alert alert-danger">
                        <i data-feather="alert-circle" class="me-2"></i>
                        ${data.error}
                    </div>
                `;
                feather.replace();
            }
        } catch (error) {
            console.error('AI suggestions error:', error);
            document.getElementById('ai-modal-content').innerHTML = `
                <div class="alert alert-danger">
                    <i data-feather="alert-circle" class="me-2"></i>
                    Failed to get AI suggestions. Please check your connection and try again.
                </div>
            `;
            feather.replace();
        } finally {
            if (button) {
                button.innerHTML = originalText;
                button.disabled = false;
                feather.replace();
            }
        }
    }
    
    displayAISuggestions(suggestions, originalText) {
        let content = `
            <div class="mb-4">
                <h6 class="text-muted mb-2">
                    <i data-feather="file-text" class="me-1"></i>
                    Original Text:
                </h6>
                <div class="bg-secondary bg-opacity-25 p-3 rounded border">
                    <p class="mb-0">${this.escapeHtml(originalText)}</p>
                </div>
            </div>
        `;
        
        if (suggestions.improved_text) {
            content += `
                <div class="mb-4">
                    <h6 class="text-info mb-2">
                        <i data-feather="edit-3" class="me-1"></i>
                        AI-Enhanced Version:
                    </h6>
                    <div class="bg-info bg-opacity-15 p-3 rounded border border-info" id="suggestion-text">
                        <p class="mb-0">${this.escapeHtml(suggestions.improved_text)}</p>
                    </div>
                </div>
            `;
            
            if (suggestions.explanation) {
                content += `
                    <div class="mb-4">
                        <h6 class="text-secondary mb-2">
                            <i data-feather="info" class="me-1"></i>
                            What Changed:
                        </h6>
                        <div class="alert alert-secondary border">
                            <p class="mb-0">${this.escapeHtml(suggestions.explanation)}</p>
                        </div>
                    </div>
                `;
            }
            
            if (suggestions.key_improvements) {
                content += `
                    <div class="mb-4">
                        <h6 class="text-success mb-2">
                            <i data-feather="check-circle" class="me-1"></i>
                            Key Improvements:
                        </h6>
                        <div class="alert alert-success border">
                            <p class="mb-0">${this.escapeHtml(suggestions.key_improvements)}</p>
                        </div>
                    </div>
                `;
            }
            
            if (suggestions.narration_notes) {
                content += `
                    <div class="mb-4">
                        <h6 class="text-warning mb-2">
                            <i data-feather="mic" class="me-1"></i>
                            Narration Notes:
                        </h6>
                        <div class="alert alert-warning border">
                            <p class="mb-0">${this.escapeHtml(suggestions.narration_notes)}</p>
                        </div>
                    </div>
                `;
            }
            
            this.currentSuggestion = {
                original: originalText,
                improved: suggestions.improved_text
            };
            
            document.getElementById('apply-suggestion-btn').style.display = 'inline-block';
        }
        
        // Handle other suggestion types
        if (suggestions.expanded_text) {
            content += `
                <div class="mb-4">
                    <h6 class="text-success mb-2">
                        <i data-feather="plus-square" class="me-1"></i>
                        Expanded Version:
                    </h6>
                    <div class="bg-success bg-opacity-15 p-3 rounded border border-success" id="suggestion-text">
                        <p class="mb-0">${this.escapeHtml(suggestions.expanded_text)}</p>
                    </div>
                </div>
            `;
            
            this.currentSuggestion = {
                original: originalText,
                improved: suggestions.expanded_text
            };
        }
        
        if (suggestions.summary) {
            content += `
                <div class="mb-4">
                    <h6 class="text-warning mb-2">
                        <i data-feather="minus-square" class="me-1"></i>
                        Summary:
                    </h6>
                    <div class="bg-warning bg-opacity-15 p-3 rounded border border-warning" id="suggestion-text">
                        <p class="mb-0">${this.escapeHtml(suggestions.summary)}</p>
                    </div>
                </div>
            `;
            
            this.currentSuggestion = {
                original: originalText,
                improved: suggestions.summary
            };
        }
        
        document.getElementById('ai-modal-content').innerHTML = content;
        feather.replace();
    }
    
    applySuggestion() {
        if (!this.currentSuggestion) return;
        
        const editor = tinymce.get('editor-content');
        if (!editor) return;
        
        const content = editor.getContent();
        const newContent = content.replace(this.currentSuggestion.original, this.currentSuggestion.improved);
        editor.setContent(newContent);
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('aiSuggestionsModal'));
        modal.hide();
        
        this.showNotification('AI suggestion applied successfully!', 'success');
        this.updateWordCount();
        this.scheduleAutoSave();
        
        // Clear current suggestion
        this.currentSuggestion = null;
    }
    
    async updateStatus(newStatus) {
        try {
            const response = await fetch(`/editor/update_status/${this.projectId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    status: newStatus
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification(data.message, 'success');
                // Update the status badge
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                this.showNotification(data.error || 'Failed to update status', 'error');
            }
        } catch (error) {
            console.error('Status update error:', error);
            this.showNotification('Error updating status', 'error');
        }
    }
    
    async uploadPDF(file) {
        const formData = new FormData();
        formData.append('pdf_file', file);
        
        this.showNotification('Uploading and processing PDF...', 'info');
        
        try {
            const response = await fetch(`/editor/upload_pdf/${this.projectId}`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification(data.message, 'success');
                
                // Add extracted content to editor
                if (data.extracted_text) {
                    const editor = tinymce.get('editor-content');
                    if (editor) {
                        const currentContent = editor.getContent();
                        const newContent = currentContent + '\n\n<h3>--- Imported from PDF ---</h3>\n\n' + data.extracted_text;
                        editor.setContent(newContent);
                        this.updateWordCount();
                        this.scheduleAutoSave();
                    }
                }
            } else {
                this.showNotification(data.error || 'Failed to process PDF', 'error');
            }
        } catch (error) {
            console.error('PDF upload error:', error);
            this.showNotification('Error uploading PDF', 'error');
        }
        
        // Clear file input
        file.value = '';
    }
    
    showNotification(message, type = 'info') {
        const alertClass = {
            'error': 'alert-danger',
            'success': 'alert-success',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';
        
        const iconName = {
            'error': 'alert-circle',
            'success': 'check-circle',
            'warning': 'alert-triangle',
            'info': 'info'
        }[type] || 'info';
        
        const alert = document.createElement('div');
        alert.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px; max-width: 500px;';
        alert.innerHTML = `
            <i data-feather="${iconName}" class="me-2"></i>
            ${this.escapeHtml(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alert);
        feather.replace();
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Export functionality
    exportToText() {
        const editor = tinymce.get('editor-content');
        if (!editor) return;
        
        const content = editor.getContent({ format: 'text' });
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `manuscript-${this.projectId}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('Manuscript exported as text file', 'success');
    }
    
    exportToHTML() {
        const editor = tinymce.get('editor-content');
        if (!editor) return;
        
        const content = editor.getContent();
        const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manuscript - Project ${this.projectId}</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1, h2, h3, h4, h5, h6 { margin-top: 1.5em; margin-bottom: 0.5em; }
        p { margin-bottom: 1em; }
    </style>
</head>
<body>
    ${content}
</body>
</html>
        `;
        
        const blob = new Blob([htmlContent], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `manuscript-${this.projectId}.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('Manuscript exported as HTML file', 'success');
    }
}

// Global functions that can be called from HTML
window.mysticEditor = null;

function initializeMysticEditor(projectId) {
    if (window.mysticEditor) {
        console.log('Editor already initialized');
        return;
    }
    
    window.mysticEditor = new MysticEditor(projectId);
}

function saveProject(autoSave = false) {
    if (window.mysticEditor) {
        window.mysticEditor.saveProject(autoSave);
    }
}

function getAISuggestions(type) {
    if (window.mysticEditor) {
        window.mysticEditor.getAISuggestions(type);
    }
}

function applySuggestion() {
    if (window.mysticEditor) {
        window.mysticEditor.applySuggestion();
    }
}

function updateStatus(status) {
    if (window.mysticEditor) {
        window.mysticEditor.updateStatus(status);
    }
}

function exportManuscript(format) {
    if (window.mysticEditor) {
        if (format === 'text') {
            window.mysticEditor.exportToText();
        } else if (format === 'html') {
            window.mysticEditor.exportToHTML();
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Auto-initialize if projectId is available globally
    if (typeof projectId !== 'undefined') {
        initializeMysticEditor(projectId);
    }
});
