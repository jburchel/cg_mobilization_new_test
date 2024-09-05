document.addEventListener('DOMContentLoaded', function() {
    const taskLists = document.querySelectorAll('.task-list');
    const taskCards = document.querySelectorAll('.task-card');

    taskCards.forEach(card => {
        card.addEventListener('dragstart', dragStart);
        card.addEventListener('dragend', dragEnd);
    });

    taskLists.forEach(list => {
        list.addEventListener('dragover', dragOver);
        list.addEventListener('dragenter', dragEnter);
        list.addEventListener('dragleave', dragLeave);
        list.addEventListener('drop', drop);
    });

    function dragStart(e) {
        e.dataTransfer.setData('text/plain', e.target.dataset.taskId);
        setTimeout(() => {
            e.target.classList.add('dragging');
        }, 0);
    }

    function dragEnd(e) {
        e.target.classList.remove('dragging');
    }

    function dragOver(e) {
        e.preventDefault();
    }

    function dragEnter(e) {
        e.preventDefault();
        if (e.target.classList.contains('task-list')) {
            e.target.classList.add('drag-over');
        }
    }

    function dragLeave(e) {
        if (e.target.classList.contains('task-list')) {
            e.target.classList.remove('drag-over');
        }
    }

    function drop(e) {
        e.preventDefault();
        const taskList = e.target.closest('.task-list');
        if (taskList) {
            taskList.classList.remove('drag-over');
            const taskId = e.dataTransfer.getData('text');
            const draggableElement = document.querySelector(`[data-task-id="${taskId}"]`);
            const sourceList = draggableElement.parentElement;

            // Move the task card immediately
            taskList.appendChild(draggableElement);

            // Update "No tasks" message for both source and target lists immediately
            updateNoTasksMessage(sourceList);
            updateNoTasksMessage(taskList);

            // Update the server
            updateTaskStatus(taskId, taskList.id, sourceList, draggableElement);
        }
    }

    function updateTaskStatus(taskId, newStatus, sourceList, taskElement) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        fetch(`/task-tracker/${taskId}/update-status/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `status=${newStatus}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.status !== 'success') {
                console.error('Failed to update task status');
                // Revert the change if the server update fails
                sourceList.appendChild(taskElement);
                updateNoTasksMessage(sourceList);
                updateNoTasksMessage(taskElement.parentElement);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            // Revert the change if there's an error
            sourceList.appendChild(taskElement);
            updateNoTasksMessage(sourceList);
            updateNoTasksMessage(taskElement.parentElement);
        });
    }

    function updateNoTasksMessage(taskList) {
        const noTasksMessage = taskList.querySelector('.no-tasks-message');
        const hasTasks = taskList.querySelector('.task-card');

        if (noTasksMessage) {
            noTasksMessage.style.display = hasTasks ? 'none' : 'block';
        } else if (!hasTasks) {
            const newMessage = document.createElement('p');
            newMessage.classList.add('no-tasks-message');
            newMessage.textContent = 'No tasks in this status.';
            taskList.appendChild(newMessage);
        }
    }

    // Initialize "No tasks" messages on page load
    taskLists.forEach(updateNoTasksMessage);
});