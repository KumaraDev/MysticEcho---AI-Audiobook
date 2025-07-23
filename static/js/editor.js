/**
 * Mystic Echo Editor JavaScript
 * Handles text editing, auto-save, AI integration, and file operations
 */

class MysticEditor {
    constructor(projectId) {
        this.projectId = projectId;
        this.currentContent = '';
        this.lastSavedContent = '';
        this.autoSaveTimer = null;
        this.autoSaveInterval = 3000; // 3 seconds for more responsive auto-save
        this.currentSuggestion = null;
        this.isInitialized = false;
        this.editor = null;
        
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
        this.editor = document.getElementById('editor-content');
        if (!this.editor) {
            // Try chapter editor content if main editor not found
            this.editor = document.getElementById('chapter-editor-content');
        }
        if (this.editor) {
            this.currentContent = this.editor.value;
            this.lastSavedContent = this.currentContent;
            this.updateWordCount();
        }
    }
    
    setupEventListeners() {
        if (!this.editor) return;
        
        const self = this;
        
        // Input event for real-time updates
        this.editor.addEventListener('input', function() {
            self.currentContent = this.value;
            self.updateWordCount();
            self.scheduleAutoSave();
        });
        
        // Keyup for additional responsiveness
        this.editor.addEventListener('keyup', function() {
            self.currentContent = this.value;
            self.updateWordCount();
        });
        
        // Paste event
        this.editor.addEventListener('paste', function() {
            setTimeout(() => {
                self.currentContent = this.value;
                self.updateWordCount();
                self.scheduleAutoSave();
            }, 100);
        });
        
        // Focus events for status updates
        this.editor.addEventListener('focus', function() {
            self.showStatus('Editing...', 'info');
        });
        
        this.editor.addEventListener('blur', function() {
            if (self.currentContent !== self.lastSavedContent) {
                self.saveProject(true); // Auto-save on blur
            }
        });
    }
    
    startAutoSave() {
        const self = this;
        setInterval(() => {
            if (self.currentContent !== self.lastSavedContent && self.currentContent.trim() !== '') {
                self.saveProject(true);
            }
        }, this.autoSaveInterval);
    }
    
    scheduleAutoSave() {
        const self = this;
        clearTimeout(this.autoSaveTimer);
        
        this.showStatus('Unsaved changes...', 'warning');
        
        this.autoSaveTimer = setTimeout(() => {
            if (self.currentContent !== self.lastSavedContent) {
                self.saveProject(true);
            }
        }, 2000); // Auto-save after 2 seconds of inactivity
    }
    
    updateWordCount() {
        const content = this.currentContent || '';
        const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;
        const wordCountElement = document.getElementById('word-count');
        if (wordCountElement) {
            wordCountElement.textContent = `${wordCount} words`;
        }
    }
    
    showStatus(message, type = 'info') {
        const statusElement = document.getElementById('auto-save-status');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `text-${type === 'warning' ? 'warning' : type === 'success' ? 'success' : 'muted'}`;
        }
    }
    
    saveProject(autoSave = false) {
        const self = this;
        const saveBtn = document.getElementById('save-btn');
        
        if (!autoSave && saveBtn) {
            saveBtn.innerHTML = '<i data-feather="loader" class="me-1"></i>Saving...';
            saveBtn.disabled = true;
        }
        
        fetch(`/editor/save_project/${this.projectId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: this.currentContent,
                auto_save: autoSave
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                self.lastSavedContent = self.currentContent;
                const status = autoSave ? 'Auto-saved' : 'Saved';
                self.showStatus(status, 'success');
                
                if (!autoSave) {
                    self.showNotification('Project saved successfully!', 'success');
                }
            } else {
                self.showNotification(data.error || 'Failed to save project', 'error');
                self.showStatus('Save failed', 'danger');
            }
        })
        .catch(error => {
            console.error('Save error:', error);
            self.showNotification('Error saving project', 'error');
            self.showStatus('Save failed', 'danger');
        })
        .finally(() => {
            if (!autoSave && saveBtn) {
                saveBtn.innerHTML = '<i data-feather="save" class="me-1"></i>Save';
                saveBtn.disabled = false;
                feather.replace();
            }
        });
    }
    
    getSelectedText() {
        if (!this.editor) return '';
        
        const start = this.editor.selectionStart;
        const end = this.editor.selectionEnd;
        return this.editor.value.substring(start, end);
    }
    
    replaceSelectedText(newText) {
        if (!this.editor) return;
        
        const start = this.editor.selectionStart;
        const end = this.editor.selectionEnd;
        const value = this.editor.value;
        
        this.editor.value = value.substring(0, start) + newText + value.substring(end);
        this.editor.selectionStart = this.editor.selectionEnd = start + newText.length;
        
        this.currentContent = this.editor.value;
        this.updateWordCount();
        this.scheduleAutoSave();
    }
    
    showNotification(message, type) {
        const alertClass = type === 'error' ? 'alert-danger' : type === 'success' ? 'alert-success' : 'alert-info';
        const iconName = type === 'error' ? 'alert-circle' : type === 'success' ? 'check-circle' : 'info';
        
        const notification = document.createElement('div');
        notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            <i data-feather="${iconName}" class="me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        feather.replace();
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// Global functions for backward compatibility
let mysticEditor;

function initializeEditor(projectId) {
    mysticEditor = new MysticEditor(projectId);
    return mysticEditor;
}

function getAISuggestions(type) {
    if (!mysticEditor) return;
    
    const selectedText = mysticEditor.getSelectedText();
    
    if (!selectedText.trim()) {
        mysticEditor.showNotification('Please select some text first', 'warning');
        return;
    }
    
    const modal = new bootstrap.Modal(document.getElementById('aiSuggestionsModal'));
    modal.show();
    
    fetch(`/editor/ai_suggestions/${mysticEditor.projectId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: selectedText,
            type: type
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayAISuggestions(data.suggestions, selectedText);
        } else {
            document.getElementById('ai-modal-content').innerHTML = `
                <div class="alert alert-danger">
                    <i data-feather="alert-circle" class="me-2"></i>
                    ${data.error}
                </div>
            `;
            feather.replace();
        }
    })
    .catch(error => {
        console.error('AI suggestions error:', error);
        document.getElementById('ai-modal-content').innerHTML = `
            <div class="alert alert-danger">
                <i data-feather="alert-circle" class="me-2"></i>
                Failed to get AI suggestions
            </div>
        `;
        feather.replace();
    });
}

function displayAISuggestions(suggestions, originalText) {
    let content = `
        <div class="mb-3">
            <h6>Original Text:</h6>
            <div class="bg-light bg-opacity-10 p-3 rounded">${originalText}</div>
        </div>
    `;
    
    if (suggestions.improved_text) {
        content += `
            <div class="mb-3">
                <h6>Improved Version:</h6>
                <div class="bg-info bg-opacity-10 p-3 rounded" id="suggestion-text">${suggestions.improved_text}</div>
            </div>
        `;
        
        if (suggestions.explanation) {
            content += `
                <div class="mb-3">
                    <h6>Explanation:</h6>
                    <p class="text-muted">${suggestions.explanation}</p>
                </div>
            `;
        }
        
        mysticEditor.currentSuggestion = {
            original: originalText,
            improved: suggestions.improved_text
        };
        
        document.getElementById('apply-suggestion-btn').style.display = 'inline-block';
    }
    
    document.getElementById('ai-modal-content').innerHTML = content;
}

function applySuggestion() {
    if (!mysticEditor || !mysticEditor.currentSuggestion) return;
    
    const content = mysticEditor.editor.value;
    const newContent = content.replace(mysticEditor.currentSuggestion.original, mysticEditor.currentSuggestion.improved);
    mysticEditor.editor.value = newContent;
    mysticEditor.currentContent = newContent;
    
    const modal = bootstrap.Modal.getInstance(document.getElementById('aiSuggestionsModal'));
    modal.hide();
    
    mysticEditor.showNotification('Suggestion applied successfully!', 'success');
    mysticEditor.updateWordCount();
    mysticEditor.scheduleAutoSave();
}

// Global function for updateWordCount for backward compatibility
function updateWordCount() {
    if (mysticEditor) {
        mysticEditor.updateWordCount();
    }
}

function updateStatus(newStatus) {
    if (!mysticEditor) return;
    
    fetch(`/editor/update_status/${mysticEditor.projectId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            status: newStatus
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            mysticEditor.showNotification(data.error || 'Failed to update status', 'error');
        }
    })
    .catch(error => {
        console.error('Status update error:', error);
        mysticEditor.showNotification('Error updating status', 'error');
    });
}

function uploadPDF(file) {
    if (!mysticEditor) return;
    
    const formData = new FormData();
    formData.append('pdf_file', file);
    
    mysticEditor.showNotification('Uploading and processing PDF...', 'info');
    
    fetch(`/editor/upload_pdf/${mysticEditor.projectId}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mysticEditor.showNotification(data.message, 'success');
            // Reload the page to show the imported content
            location.reload();
        } else {
            mysticEditor.showNotification(data.error || 'Failed to process PDF', 'error');
        }
    })
    .catch(error => {
        console.error('PDF upload error:', error);
        mysticEditor.showNotification('Error uploading PDF', 'error');
    });
}

function saveProject(autoSave = false) {
    if (!mysticEditor) return;
    mysticEditor.saveProject(autoSave);
}