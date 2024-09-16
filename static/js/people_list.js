document.addEventListener('DOMContentLoaded', function() {
    let draggedItem = null;
    let sourceStage = null;
    const dragFeedback = document.getElementById('dragFeedback');
    const errorMessage = document.getElementById('errorMessage');

    function initDragAndDrop() {
        document.querySelectorAll('.person-card').forEach(card => {
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
            updatePersonStage(draggedItem.dataset.personId, newStage, this, sourceStage);
        }
    }

    function updatePersonStage(personId, newStage, targetStage, sourceStage) {
        fetch('/contacts/update_pipeline_stage/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                person_id: personId,
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
                throw new Error(data.error || 'Failed to update person stage');
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
        const personCards = stageContent.querySelectorAll('.person-card');

        if (personCards.length === 0) {
            if (!emptyMessage) {
                const newEmptyMessage = document.createElement('p');
                newEmptyMessage.className = 'empty-stage';
                newEmptyMessage.textContent = 'No people in this stage.';
                stageContent.appendChild(newEmptyMessage);
            }
        } else {
            if (emptyMessage) {
                emptyMessage.remove();
            }
        }
    }

    function updatePipelineSummary() {
        fetch('/contacts/get-people-pipeline-summary/')
        .then(response => response.json())
        .then(data => {
            console.log('Pipeline summary updated:', data);
            
            // Update total people
            const totalElement = document.querySelector('.summary-item.total-item .summary-value');
            if (totalElement) {
                totalElement.textContent = data.total_people;
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
        if (dragFeedback) {
            dragFeedback.style.display = 'block';
        }
    }

    function hideDragFeedback() {
        if (dragFeedback) {
            dragFeedback.style.display = 'none';
        }
    }

    function showErrorMessage(message) {
        if (errorMessage) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 5000);
        }
    }

    // Initialize drag and drop
    initDragAndDrop();

    // Add search functionality
    const searchInput = document.getElementById('peopleSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            document.querySelectorAll('.person-card').forEach(card => {
                const personName = card.querySelector('h3').textContent.toLowerCase();
                card.style.display = personName.includes(searchTerm) ? 'block' : 'none';
            });

            // Update empty stage messages after search
            document.querySelectorAll('.pipeline-stage').forEach(updateEmptyStageMessage);
        });
    }

    // Add stage toggle functionality
    document.querySelectorAll('.stage-header').forEach(header => {
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            const isExpanded = content.style.display !== 'none';
            content.style.display = isExpanded ? 'none' : 'block';
            this.querySelector('h2').textContent = isExpanded ? '▶ ' + this.textContent.slice(2) : '▼ ' + this.textContent.slice(2);
        });
    });
});