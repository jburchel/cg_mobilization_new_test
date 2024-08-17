document.addEventListener('DOMContentLoaded', function() {
    let draggedItem = null;
    let sourceStage = null;

    function initDragAndDrop() {
        document.querySelectorAll('.church-card').forEach(card => {
            card.addEventListener('dragstart', function(e) {
                // Prevent drag if clicking on a link
                if (e.target.closest('.church-name-link, .church-image-link')) {
                    e.preventDefault();
                    return;
                }
                draggedItem = this;
                sourceStage = this.closest('.pipeline-stage');
                setTimeout(() => this.style.opacity = '0.5', 0);
            });

            card.addEventListener('dragend', function() {
                this.style.opacity = '1';
            });

            // Prevent default drag behavior on links
            card.querySelectorAll('.church-name-link, .church-image-link').forEach(link => {
                link.addEventListener('mousedown', function(e) {
                    e.stopPropagation();
                });
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
                    updatePipelineStage(draggedItem.dataset.churchId, newStage, this, sourceStage);
                }
            });
        });
    }

    function updatePipelineStage(churchId, newStage, targetStage, sourceStage) {
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
                console.log('Successfully updated church pipeline stage');
                setTimeout(() => {
                    window.location.reload();
                }, 100);
            } else {
                console.error('Failed to update church pipeline stage:', data.error);
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