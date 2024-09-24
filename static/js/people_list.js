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
            const newStage = this.getAttribute('stage');
            updatePersonStage(draggedItem.getAttribute('person-id'), newStage, this, sourceStage);
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
                updatePipelineSummary(data.summary);
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

    function updatePipelineSummary(summary) {
        Object.entries(summary).forEach(([stage, count]) => {
            const summaryItem = document.querySelector(`.summary-item[stage="${stage}"] .summary-value`);
            if (summaryItem) {
                summaryItem.textContent = count;
            }
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

    function initializeStageToggles() {
        document.querySelectorAll('.stage-header').forEach(header => {
            header.addEventListener('click', function() {
                const content = this.nextElementSibling;
                const icon = this.querySelector('.toggle-icon');
                
                if (content.style.display === 'block') {
                    content.style.display = 'none';
                    icon.textContent = '▶';
                } else {
                    content.style.display = 'block';
                    icon.textContent = '▼';
                }
            });
        });
    }

    // Initialize drag and drop
    initDragAndDrop();

    // Initialize stage toggles
    initializeStageToggles();

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
});