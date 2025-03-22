/**
 * Charts Data Handler
 * This script fetches real data from the backend and updates all dashboard charts
 */

document.addEventListener('DOMContentLoaded', function() {
  // Fetch chart data from API
  fetchChartData();

  // Setup refresh button behavior
  const refreshBtn = document.getElementById('refresh-btn');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', function() {
      fetchChartData();
    });
  }

  // Fetch data every 60 seconds
  setInterval(fetchChartData, 60000);
});

// Charts instances to be updated
let processingTimeChart = null;
let transformationTypesChart = null;
let errorTypesChart = null;

/**
 * Initialize all charts with initial data
 */
function initializeCharts() {
  // Initialize Processing Time Chart
  const timeCtx = document.getElementById('processing-time-chart')?.getContext('2d');
  if (timeCtx) {
    processingTimeChart = new Chart(timeCtx, {
      type: 'line',
      data: {
        labels: ['Loading...'],
        datasets: [{
          label: 'Avg Processing Time (s)',
          data: [0],
          borderColor: '#4BBEB3',
          backgroundColor: 'rgba(75, 190, 179, 0.1)',
          fill: true,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }
  
  // Initialize Transformation Types Chart
  const typesCtx = document.getElementById('transformation-types-chart')?.getContext('2d');
  if (typesCtx) {
    transformationTypesChart = new Chart(typesCtx, {
      type: 'doughnut',
      data: {
        labels: ['Loading...'],
        datasets: [{
          data: [1],
          backgroundColor: ['#cccccc']
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: {
              boxWidth: 12,
              padding: 15
            }
          }
        }
      }
    });
  }
  
  // Initialize Error Types Chart
  const errorCtx = document.getElementById('error-types-chart')?.getContext('2d');
  if (errorCtx) {
    errorTypesChart = new Chart(errorCtx, {
      type: 'bar',
      data: {
        labels: ['Loading...'],
        datasets: [{
          label: 'Error Count',
          data: [0],
          backgroundColor: ['#cccccc']
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }
}

/**
 * Fetch chart data from the API
 */
function fetchChartData() {
  // If charts aren't initialized yet, initialize them
  if (!processingTimeChart && !transformationTypesChart && !errorTypesChart) {
    initializeCharts();
  }
  
  // Show loading state
  showLoadingState();
  
  // Fetch all data from the API
  fetch('/api/dashboard-data')
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      updateCharts(data);
      hideLoadingState();
    })
    .catch(error => {
      console.error('Error fetching dashboard data:', error);
      hideLoadingState();
    });
}

/**
 * Update all charts with new data
 */
function updateCharts(data) {
  // Update Processing Time Chart
  if (processingTimeChart && data.processingTimes) {
    processingTimeChart.data.labels = data.processingTimes.labels;
    processingTimeChart.data.datasets[0].data = data.processingTimes.values;
    processingTimeChart.update();
  }
  
  // Update Transformation Types Chart
  if (transformationTypesChart && data.transformationTypes) {
    transformationTypesChart.data.labels = data.transformationTypes.labels;
    transformationTypesChart.data.datasets[0].data = data.transformationTypes.values;
    transformationTypesChart.data.datasets[0].backgroundColor = [
      '#4BBEB3', // XML to XML
      '#4B86B4', // JSON to XML
      '#ADCBE3'  // CSV to XML
    ];
    transformationTypesChart.update();
  }
  
  // Update Error Types Chart
  if (errorTypesChart && data.errorTypes) {
    errorTypesChart.data.labels = data.errorTypes.labels;
    errorTypesChart.data.datasets[0].data = data.errorTypes.values;
    errorTypesChart.data.datasets[0].backgroundColor = [
      '#FF6B6B', '#F7A072', '#F9C74F', '#90BE6D', '#577590'
    ].slice(0, data.errorTypes.labels.length);
    errorTypesChart.update();
  }
}

/**
 * Show loading state on charts
 */
function showLoadingState() {
  const chartCards = document.querySelectorAll('.chart-card');
  chartCards.forEach(card => {
    if (!card.querySelector('.chart-loading')) {
      const loadingEl = document.createElement('div');
      loadingEl.className = 'chart-loading';
      loadingEl.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
      card.appendChild(loadingEl);
    }
  });
}

/**
 * Hide loading state on charts
 */
function hideLoadingState() {
  document.querySelectorAll('.chart-loading').forEach(el => el.remove());
} 