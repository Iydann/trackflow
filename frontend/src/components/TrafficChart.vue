<template>
  <div class="chart-container">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  Title,
  CategoryScale,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

// Register Chart.js components
Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  Title,
  CategoryScale,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps({
  timeSeries: {
    type: Array,
    required: true
  },
  showCrossed: {
    type: Boolean,
    default: false
  }
})

const chartCanvas = ref(null)
let chartInstance = null

const createChart = () => {
  if (!chartCanvas.value || !props.timeSeries || props.timeSeries.length === 0) return

  // Destroy existing chart
  if (chartInstance) {
    chartInstance.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')
  
  const labels = props.timeSeries.map(d => `Menit ${d.minute}`)
  const vehiclesData = props.timeSeries.map(d => d.vehicles)
  const crossedData = props.timeSeries.map(d => d.crossed || 0)

  const datasets = [
    {
      label: 'Total Kendaraan Terdeteksi',
      data: vehiclesData,
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.3,
      fill: true,
      pointRadius: 4,
      pointHoverRadius: 6
    }
  ]

  if (props.showCrossed && crossedData.some(v => v > 0)) {
    datasets.push({
      label: 'Kendaraan Melewati Garis',
      data: crossedData,
      borderColor: 'rgb(234, 179, 8)',
      backgroundColor: 'rgba(234, 179, 8, 0.1)',
      tension: 0.3,
      fill: true,
      pointRadius: 4,
      pointHoverRadius: 6
    })
  }

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        title: {
          display: true,
          text: 'Vehicles per Minute',
          font: {
            size: 16,
            weight: 'bold'
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          callbacks: {
            label: function(context) {
              return `${context.dataset.label}: ${context.parsed.y} vehicles`
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          },
          title: {
            display: true,
            text: 'Vehicles'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Waktu (Menit)'
          }
        }
      },
      interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
      }
    }
  })
}

onMounted(() => {
  createChart()
})

watch(() => props.timeSeries, () => {
  createChart()
}, { deep: true })
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 400px;
  width: 100%;
}
</style>
