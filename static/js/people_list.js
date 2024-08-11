document.addEventListener('DOMContentLoaded', function() {
    const pipelineGrid = document.querySelector('.pipeline-grid');
    let draggedItem = null;

    // Add drag start event listener to all person cards
    document.querySelectorAll('.person-card').forEach(card => {
        card.addEventListener('dragstart', function(e) {
            draggedItem = this;
            setTimeout(() => this.style.display = 'none', 0);
        });

        card.addEventListener('dragend', function() {
            setTimeout(() => this.style.display = '', 0);
            draggedItem = null;
        });
    });

    // Add drag over and drop event listeners to all pipeline stages
    document.querySelectorAll('.pipeline-stage').forEach(stage => {
        stage.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.style.background = 'rgba(0, 0, 0, 0.1)';
        });

        stage.addEventListener('dragleave', function() {
            this.style.background = '';
        });

        stage.addEventListener('drop', function(e) {
            e.preventDefault();
            this.style.background = '';
            if (draggedItem) {
                this.querySelector('.stage-content').appendChild(draggedItem);
                updatePipelineStage(draggedItem.dataset.personId, this.dataset.stage);
            }
        });
    });

    function updatePipelineStage(personId, newStage) {
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
                // Update counts here if needed
            } else {
                console.error('Failed to update pipeline stage');
                // Handle error, maybe move the card back
            }
        })
        .catch(error => {
            console.error('Error:', error);
            // Handle error, maybe move the card back
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

    // Collapsible functionality
    document.querySelectorAll('.stage-header').forEach(function(header) {
        header.addEventListener('click', function() {
            var stage = this.closest('.pipeline-stage');
            stage.classList.toggle('collapsed');
            
            // Recalculate flex basis for expanded columns
            var expandedColumns = document.querySelectorAll('.pipeline-stage:not(.collapsed)');
            var flexBasis = 100 / expandedColumns.length + '%';
            expandedColumn

s.forEach(function(col) {
                col.style.flex = '1 1 ' + flexBasis;
            });
        });
    });
});