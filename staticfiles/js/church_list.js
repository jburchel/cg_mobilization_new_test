document.addEventListener('DOMContentLoaded', function() {
    let draggedItem = null;
    let sourceStage = null;
    const dragFeedback = document.getElementById('dragFeedback');
    const errorMessage = document.getElementById('errorMessage');

    function initDragAndDrop() {
        document.querySelectorAll('.church-card').forEach(card => {
            card.addEventListener('dragstart', handleDragStart);
            card.addEventListener('dragend', handleDragEnd);
        });

        document.querySelectorAll('.pipeline-stage').forEach(stage => {
            stage.addEventListener('dragover', handleDragOver);
            stage.addEventListener('dragleave', handleDragLeave);
            stage.addEventListener('drop', handleDrop);
        });
    }

    function handleDragStart(e) {
        draggedItem = this;
        sourceStage = this.closest('.pipeline-stage');
        setTimeout(() => this.style.opacity = '0.5', 0);
        showDragFeedback();
    }

    function handleDragEnd() {
        this.style.opacity = '1';
        hideDragFeedback();
    }

    function handleDragOver(e) {
        e.preventDefault();
        this.classList.add('drag-over');
    }

    function handleDragLeave() {
        this.classList.remove('drag-over');
    }

    function handleDrop(e) {
        e.preventDefault();
        this.classList.remove('drag-over');
        if (draggedItem && this !== sourceStage) {
            const newStage = this.dataset.stage;
            updateChurchStage(draggedItem.dataset.churchId, newStage, this, sourceStage);
        }
    }

    function updateChurchStage(churchId, newStage, targetStage, sourceStage) {
        fetch('/contacts/update_church_pipeline_stage/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                church_id: churchId,
                new_stage: newStage
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                targetStage.querySelector('.stage-content').appendChild(draggedItem);
                updateEmptyStageMessage(targetStage);
                updateEmptyStageMessage(sourceStage);
                updatePipelineSummary();
            } else {
                throw new Error(data.error || 'Failed to update church stage');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            sourceStage.querySelector('.stage-content').appendChild(draggedItem);
            showErrorMessage(error.message);
        });
    }

    function updateEmptyStageMessage(stage) {
        const stageContent = stage.querySelector('.stage-content');
        const emptyMessage = stageContent.querySelector('.empty-stage');
        const visibleChurchCards = stageContent.querySelectorAll('.church-card[style="display: block;"]');

        if (visibleChurchCards.length === 0) {
            if (!emptyMessage) {
                const newEmptyMessage = document.createElement('p');
                newEmptyMessage.className = 'empty-stage';
                newEmptyMessage.textContent = 'No churches in this stage.';
                stageContent.appendChild(newEmptyMessage);
            } else {
                emptyMessage.style.display = 'block';
            }
        } else if (emptyMessage) {
            emptyMessage.style.display = 'none';
        }
    }

    function updatePipelineSummary() {
        fetch('/contacts/get-church-pipeline-summary/')
        .then(response => response.json())
        .then(data => {
            console.log('Pipeline summary updated:', data);
            
            // Update total churches
            const totalElement = document.querySelector('.summary-item.total-item .summary-value');
            if (totalElement) {
                totalElement.textContent = data.total_churches;
            }
    
            // Update individual stage counts
            Object.entries(data.pipeline_summary).forEach(([stage, count]) => {
                const stageElement = document.querySelector(`.summary-item[data-stage="${stage}"] .summary-value`);
                if (stageElement) {
                    stageElement.textContent = count;
                }
            });
        })
        .catch(error => {
            console.error('Error updating pipeline summary:', error);
            showErrorMessage('Failed to update pipeline summary');
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function showDragFeedback() {
        dragFeedback.style.display = 'block';
    }

    function hideDragFeedback() {
        dragFeedback.style.display = 'none';
    }

    function showErrorMessage(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }

    // Initialize drag and drop
    initDragAndDrop();

    // Add search functionality
    const searchInput = document.getElementById('churchSearch');
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        let matchFound = false;

        document.querySelectorAll('.pipeline-stage').forEach(stage => {
            const stageHeader = stage.querySelector('.stage-header');
            const stageContent = stage.querySelector('.stage-content');
            const toggleIcon = stageHeader.querySelector('.toggle-icon');
            let stageMatchFound = false;

            stage.querySelectorAll('.church-card').forEach(card => {
                const churchName = card.querySelector('h3').textContent.toLowerCase();
                const isMatch = churchName.includes(searchTerm);
                card.style.display = isMatch ? 'block' : 'none';
                if (isMatch) {
                    stageMatchFound = true;
                    matchFound = true;
                }
            });

            if (stageMatchFound || searchTerm === '') {
                stageContent.style.display = 'block';
                toggleIcon.textContent = '▼';
            } else {
                stageContent.style.display = 'none';
                toggleIcon.textContent = '▶';
            }

            updateEmptyStageMessage(stage);
        });

        // Show a message if no matches are found
        const noMatchMessage = document.getElementById('noMatchMessage');
        if (noMatchMessage) {
            noMatchMessage.style.display = matchFound || searchTerm === '' ? 'none' : 'block';
        }
    });

    // Add stage toggle functionality
    document.querySelectorAll('.stage-header').forEach(header => {
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            const toggleIcon = this.querySelector('.toggle-icon');
            const isExpanded = content.style.display !== 'none';
            
            content.style.display = isExpanded ? 'none' : 'block';
            toggleIcon.textContent = isExpanded ? '▶' : '▼';
        });
    });

    // Initialize stage content visibility
    document.querySelectorAll('.stage-content').forEach(content => {
        content.style.display = 'none';
    });
});
