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
            const dropzone = taskList;
            dropzone.appendChild(draggableElement);
            updateTaskStatus(taskId, taskList.id);
        }
    }

    function updateTaskStatus(taskId, newStatus) {
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
            if (data.status === 'success') {
                console.log('Task status updated successfully');
            } else {
                console.error('Failed to update task status');
                // You might want to move the card back if the update fails
            }
        })
        .catch(error => {
            console.error('Error:', error);
            // You might want to move the card back if there's an error
        });
    }
});