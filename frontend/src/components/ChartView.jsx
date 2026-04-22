import {
  Chart as ChartJS,
  CategoryScale, LinearScale,
  BarElement, LineElement, PointElement, ArcElement,
  Title, Tooltip, Legend, Filler,
} from 'chart.js'
import { Bar, Line, Pie } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale, LinearScale,
  BarElement, LineElement, PointElement, ArcElement,
  Title, Tooltip, Legend, Filler
)

const PALETTE = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
  '#8b5cf6', '#06b6d4', '#f97316', '#84cc16',
]

function buildDatasets(data, yFields, type) {
  return yFields.map((field, i) => ({
    label: field.replace(/_/g, ' '),
    data: data.map(r => r[field] ?? 0),
    backgroundColor: type === 'line' || type === 'area'
      ? PALETTE[i % PALETTE.length] + '33'
      : PALETTE[i % PALETTE.length] + 'cc',
    borderColor: PALETTE[i % PALETTE.length],
    borderWidth: type === 'bar' || type === 'grouped_bar' ? 0 : 2,
    fill: type === 'area',
    tension: 0.35,
    pointRadius: 3,
  }))
}

export default function ChartView({ report, thumbnail = false }) {
  const { data, chart } = report
  if (!chart) return <div className="no-chart-thumb">📋</div>
  if (!data?.length) return <div className="no-chart-thumb">—</div>

  const { type, title, x_axis, y_axis } = chart
  const labels  = data.map(r => r[x_axis] ?? '')
  const yFields = Array.isArray(y_axis) ? y_axis : [y_axis]

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: thumbnail ? 0 : 400 },
    plugins: {
      legend: {
        display: !thumbnail && yFields.length > 1,
        labels: { font: { size: 11 } },
      },
      title: {
        display: !thumbnail && !!title,
        text: title,
        font: { size: 13, weight: '600' },
        padding: { bottom: 12 },
      },
      tooltip: { enabled: !thumbnail },
    },
    scales: type === 'pie' ? undefined : {
      x: {
        display: !thumbnail,
        ticks: { font: { size: 11 }, maxRotation: 35 },
        grid: { display: false },
      },
      y: {
        display: !thumbnail,
        ticks: { font: { size: 11 } },
        grid: { color: '#f1f5f9' },
      },
    },
  }

  if (type === 'pie') {
    const singleField = yFields[0]
    const pieData = {
      labels,
      datasets: [{
        data: data.map(r => r[singleField] ?? 0),
        backgroundColor: PALETTE.map(c => c + 'cc'),
        borderColor: '#fff',
        borderWidth: 2,
      }],
    }
    return <Pie data={pieData} options={options} />
  }

  const chartData = { labels, datasets: buildDatasets(data, yFields, type) }

  if (type === 'line' || type === 'area') {
    return <Line data={chartData} options={options} />
  }

  // bar / grouped_bar
  return <Bar data={chartData} options={options} />
}
