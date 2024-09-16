/**
 * Church List Management
 * 
 * This module handles the drag-and-drop functionality for church pipeline stages,
 * as well as updating the pipeline summary and error handling.
 */

document.addEventListener('DOMContentLoaded', () => {
    const ChurchList = (() => {
        let draggedItem = null;
        let sourceStage = null;
        const dragFeedback = document.getElementById('dragFeedback');
        const errorMessageElement = document.getElementById('errorMessage');

        /**
         * Initialize drag and drop functionality
         */
        const initDragAndDrop = () => {
            document.querySelectorAll('.church-card').forEach(card => {
                card.setAttribute('draggable', 'true');
                card.addEventListener('dragstart', handleDragStart);
                card.addEventListener('dragend', handleDragEnd);
                card.addEventListener('keydown', handleKeyDown);
            });

            document.querySelectorAll('.pipeline-stage').forEach(stage => {
                stage.addEventListener('dragover', handleDragOver);
                stage.addEventListener('dragleave', handleDragLeave);
                stage.addEventListener('drop', handleDrop);
            });
        };

        /**
         * Handle the start of a drag operation
         * @param {DragEvent} e - The drag event
         */
        const handleDragStart = function(e) {
            draggedItem = this;
            sourceStage = this.closest('.pipeline-stage');
            setTimeout(() => {
                this.classList.add('dragging');
                showDragFeedback();
            }, 0);
        };

        /**
         * Handle the end of a drag operation
         */
        const handleDragEnd = function() {
            this.classList.remove('dragging');
            hideDragFeedback();
        };

        /**
         * Handle the dragover event
         * @param {DragEvent} e - The drag event
         */
        const handleDragOver = (e) => {
            e.preventDefault();
            e.currentTarget.classList.add('drag-over');
        };

        /**
         * Handle the dragleave event
         * @param {DragEvent} e - The drag event
         */
        const handleDragLeave = (e) => {
            e.currentTarget.classList.remove('drag-over');
        };

        /**
         * Handle the drop event
         * @param {DragEvent} e - The drop event
         */
        const handleDrop = function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            if (draggedItem && this !== sourceStage) {
                const newStage = this.dataset.stage;
                updateChurchStage(draggedItem.dataset.churchId, newStage, this, sourceStage);
            }
        };

        /**
         * Handle keyboard events for accessibility
         * @param {KeyboardEvent} e - The keyboard event
         */
        const handleKeyDown = function(e) {
            switch (e.key) {
                case 'Enter':
                case ' ':
                    e.preventDefault();
                    startKeyboardDrag(this);
                    break;
                case 'Escape':
                    cancelKeyboardDrag();
                    break;
                case 'ArrowLeft':
                case 'ArrowRight':
                    e.preventDefault();
                    moveKeyboardDrag(e.key);
                    break;
            }
        };

        /**
         * Start a keyboard-initiated drag operation
         * @param {HTMLElement} card - The card element
         */
        const startKeyboardDrag = (card) => {
            draggedItem = card;
            sourceStage = card.closest('.pipeline-stage');
            card.classList.add('dragging');
            showDragFeedback();
        };

        /**
         * Cancel a keyboard-initiated drag operation
         */
        const cancelKeyboardDrag = () => {
            if (draggedItem) {
                draggedItem.classList.remove('dragging');
                hideDragFeedback();
                draggedItem = null;
                sourceStage = null;
            }
        };

        /**
         * Move a card during a keyboard-initiated drag operation
         * @param {string} direction - The direction to move ('ArrowLeft' or 'ArrowRight')
         */
        const moveKeyboardDrag = (direction) => {
            if (!draggedItem) return;

            const stages = Array.from(document.querySelectorAll('.pipeline-stage'));
            const currentIndex = stages.indexOf(sourceStage);
            const newIndex = direction === 'ArrowLeft' ? currentIndex - 1 : currentIndex + 1;

            if (newIndex >= 0 && newIndex < stages.length) {
                const newStage = stages[newIndex];
                updateChurchStage(draggedItem.dataset.churchId, newStage.dataset.stage, newStage, sourceStage);
            }
        };

        /**
         * Update the church stage
         * @param {string} churchId - The ID of the church
         * @param {string} newStage - The new stage
         * @param {HTMLElement} targetStage - The target stage element
         * @param {HTMLElement} sourceStage - The source stage element
         */
        const updateChurchStage = async (churchId, newStage, targetStage, sourceStage) => {
            showLoadingIndicator(draggedItem);

            try {
                const response = await fetch('/update-church-stage/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        church_id: churchId,
                        new_stage: newStage
                    })
                });

                const data = await response.json();

                if (data.success) {
                    console.log('Successfully updated church stage');
                    targetStage.querySelector('.stage-content').appendChild(draggedItem);
                    await updatePipelineSummary();
                } else {
                    throw new Error(data.error || 'Failed to update church stage');
                }
            } catch (error) {
                console.error('Error:', error);
                sourceStage.querySelector('.stage-content').appendChild(draggedItem);
                showErrorMessage(error.message || 'An error occurred. Please try again.');
            } finally {
                hideLoadingIndicator(draggedItem);
                cancelKeyboardDrag();
            }
        };

        /**
         * Update the pipeline summary
         */
        const updatePipelineSummary = async () => {
            try {
                const response = await fetch('/get-pipeline-summary/');
                const data = await response.json();
                updateSummaryHTML(data);
            } catch (error) {
                console.error('Error updating pipeline summary:', error);
                showErrorMessage('Failed to update pipeline summary.');
            }
        };

        /**
         * Update the summary HTML
         * @param {Array} data - The summary data
         */
        const updateSummaryHTML = (data) => {
            const totalRow = document.querySelector('.pipeline-summary.total-row');
            const stagesRow = document.querySelector('.pipeline-summary.stages-row');

            totalRow.innerHTML = '';
            stagesRow.innerHTML = '';

            data.forEach((stage, index) => {
                const div = document.createElement('div');
                div.className = 'summary-item';
                div.title = stage.name;

                const label = document.createElement('span');
                label.className = 'summary-label';
                label.textContent = index === 0 ? stage.name : stage.name.slice(0, 15) + (stage.name.length > 15 ? '...' : '');

                const value = document.createElement('span');
                value.className = 'summary-value';
                value.textContent = stage.count;

                div.appendChild(label);
                div.appendChild(value);

                if (index === 0) {
                    div.classList.add('total-item');
                    totalRow.appendChild(div);
                } else {
                    stagesRow.appendChild(div);
                }
            });
        };

        /**
         * Get a cookie by name
         * @param {string} name - The name of the cookie
         * @returns {string|null} The cookie value or null if not found
         */
        const getCookie = (name) => {
            const cookieValue = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
            return cookieValue ? cookieValue.pop() : null;
        };

        /**
         * Show a loading indicator on an element
         * @param {HTMLElement} element - The element to show the loading indicator on
         */
        const showLoadingIndicator = (element) => {
            const indicator = document.createElement('div');
            indicator.className = 'loading-indicator';
            indicator.textContent = 'Updating...';
            element.appendChild(indicator);
        };

        /**
         * Hide the loading indicator from an element
         * @param {HTMLElement} element - The element to hide the loading indicator from
         */
        const hideLoadingIndicator = (element) => {
            const indicator = element.querySelector('.loading-indicator');
            if (indicator) {
                indicator.remove();
            }
        };

        /**
         * Show an error message
         * @param {string} message - The error message to display
         */
        const showErrorMessage = (message) => {
            errorMessageElement.textContent = message;
            errorMessageElement.style.display = 'block';
            errorMessageElement.setAttribute('aria-hidden', 'false');
            setTimeout(() => {
                errorMessageElement.style.display = 'none';
                errorMessageElement.setAttribute('aria-hidden', 'true');
            }, 5000);
        };

        /**
         * Show drag feedback
         */
        const showDragFeedback = () => {
            dragFeedback.style.display = 'block';
            dragFeedback.setAttribute('aria-hidden', 'false');
        };

        /**
         * Hide drag feedback
         */
        const hideDragFeedback = () => {
            dragFeedback.style.display = 'none';
            dragFeedback.setAttribute('aria-hidden', 'true');
        };

        return {
            init: initDragAndDrop
        };
    })();

    ChurchList.init();
});