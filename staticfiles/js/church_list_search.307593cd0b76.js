document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('churchSearch');
    const pipelineStages = document.querySelectorAll('.pipeline-stage');

    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();

        pipelineStages.forEach(stage => {
            const churchCards = stage.querySelectorAll('.church-card');
            let visibleCards = 0;

            churchCards.forEach(card => {
                const name = card.dataset.name.toLowerCase();
                if (name.includes(searchTerm)) {
                    card.style.display = '';
                    visibleCards++;
                } else {
                    card.style.display = 'none';
                }
            });

            // Show/hide empty message
            const emptyMessage = stage.querySelector('.empty-stage');
            if (emptyMessage) {
                emptyMessage.style.display = visibleCards === 0 ? '' : 'none';
            }

            // Show/hide the entire stage
            stage.style.display = visibleCards === 0 ? 'none' : '';
        });

        // Update summary counts
        updateSummaryCounts();
    });

    function updateSummaryCounts() {
        const summaryItems = document.querySelectorAll('.summary-item');
        let totalVisibleCards = 0;

        summaryItems.forEach(item => {
            const stageName = item.getAttribute('title');
            const stageElement = document.querySelector(`.pipeline-stage[stage="${stageName.toLowerCase().replace(/\s+/g, '-')}"]`);
            if (stageElement) {
                const visibleCards = stageElement.querySelectorAll('.church-card[style="display: "]').length;
                item.querySelector('.summary-value').textContent = visibleCards;
                totalVisibleCards += visibleCards;
            }
        });

        // Update total count
        const totalItem = document.querySelector('.summary-item.total-item');
        if (totalItem) {
            totalItem.querySelector('.summary-value').textContent = totalVisibleCards;
        }
    }
});