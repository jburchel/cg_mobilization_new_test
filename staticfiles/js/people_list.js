document.addEventListener('DOMContentLoaded', function() {
    let draggedItem = null;
    let sourceStage = null;

    function initDragAndDrop() {
        document.querySelectorAll('.person-card').forEach(card => {
            card.addEventListener('dragstart', function(e) {
                draggedItem = this;
                sourceStage = this.closest('.pipeline-stage');
                setTimeout(() => this.style.opacity = '0.5', 0);
            });

            card.addEventListener('dragend', function() {
                this.style.opacity = '1';
            });
        });

        document.querySelectorAll('.pipeline-stage').forEach(stage => {
            stage.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.classList.add('drag-over');
            });

            stage.addEventListener('dragleave', function() {
                this.classList.remove('drag-over');
            });

            stage.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('drag-over');
                if (draggedItem && this !== sourceStage) {
                    const newStage = this.dataset.stage;
                    updatePipelineStage(draggedItem.dataset.personId, newStage, this, sourceStage);
                }
            });
        });
    }

    function updatePipelineStage(personId, newStage, targetStage, sourceStage) {
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
                console.log('Successfully updated pipeline stage');
                targetStage.querySelector('.stage-content').appendChild(draggedItem);
                updatePipelineSummary();
            } else {
                console.error('Failed to update pipeline stage:', data.error);
                sourceStage.querySelector('.stage-content').appendChild(draggedItem);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            sourceStage.querySelector('.stage-content').appendChild(draggedItem);
        });
    }

    function initCollapsible() {
        const stages = document.querySelectorAll('.pipeline-stage');
        const totalStages = stages.length;

        stages.forEach(stage => {
            const header = stage.querySelector('.stage-header');
            header.addEventListener('click', function() {
                stage.classList.toggle('collapsed');
                const arrow = this.querySelector('.collapse-arrow');
                arrow.textContent = stage.classList.contains('collapsed') ? '▶' : '▼';
                
                updateStageSizes();
            });
        });

        function updateStageSizes() {
            const collapsedStages = document.querySelectorAll('.pipeline-stage.collapsed');
            const expandedStages = document.querySelectorAll('.pipeline-stage:not(.collapsed)');
            const collapsedWidth = 40; // This should match the --collapsed-width in CSS
            
            const availableWidth = 100 - (collapsedStages.length * (collapsedWidth / 10));
            const widthPerExpanded = availableWidth / expandedStages.length;

            stages.forEach(stage => {
                if (stage.classList.contains('collapsed')) {
                    stage.style.flex = `0 0 ${collapsedWidth}px`;
                } else {
                    stage.style.flex = `1 1 ${widthPerExpanded}%`;
                }
            });
        }

        // Initial setup
        updateStageSizes();
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

    initDragAndDrop();
    initCollapsible();
});