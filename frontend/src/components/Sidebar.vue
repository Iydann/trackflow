<template>
  <aside
    :style="{ width: sidebarWidth, transition: 'width 220ms cubic-bezier(.2,.9,.2,1)' }"
    :class="[collapsed ? 'p-2 min-w-[64px]' : 'p-4 min-w-[280px]', 'flex flex-col bg-gray-100 border-r overflow-hidden', 'sticky top-[72px] self-start h-[calc(100vh-72px)]']"
  >
  <nav class="flex flex-col gap-2 mt-1">
      <Button
        v-for="(item, index) in navigationItems"
        :key="index"
        variant="ghost"
        @click="navigate(item.path)"
        :class="[ 'flex items-center gap-3 w-full text-left rounded-md', collapsed ? 'justify-center py-3' : 'px-3 py-2', isActive(item.path) ? 'bg-white font-bold' : 'hover:bg-white/60' ]"
      >
        <component :is="item.icon" class="w-5 h-5 text-gray-600" />
        <span v-if="!collapsed" class="flex-1 text-gray-700">{{ item.label }}</span>
      </Button>
    </nav>

    

  <ScrollArea class="flex-1 overflow-auto mt-3">
      <div>
        <h2 v-if="!collapsed" class="text-sm font-bold text-gray-500 mb-2">Process</h2>

        <div class="mt-0">
          <div v-for="item in processItems" :key="item.id" class="relative group">
            <div class="w-full transition-all duration-150 rounded-md" :class="isActive(item.path) ? 'bg-white font-bold' : 'group-hover:bg-white/60 group-hover:translate-x-1'">
              <Button
                variant="ghost"
                @click="navigate(item.path)"
                :class="[ 'flex items-center gap-3 w-full text-left rounded-md transition-all duration-150', collapsed ? 'py-3 justify-center' : 'px-3 py-2' ]"
              >
                <component is="BarChart3Icon" class="w-5 h-5 text-gray-600 transition-transform duration-150 group-hover:scale-110" />
                <span v-if="!collapsed" class="flex-1 text-gray-700">{{ item.name }}</span>
              </Button>
            </div>
          </div>
        </div>

        <h2 v-if="!collapsed" class="text-sm font-bold text-gray-500 mt-4">History ({{ historyItems.length }})</h2>

        <div class="mt-2 space-y-1">
          <div
            v-for="h in historyItems"
            :key="h.id"
            class="relative"
          >
            <div class="flex items-center gap-3 rounded-md" :class="collapsed ? 'justify-center' : ''">
              <Button
                variant="ghost"
                @click="navigate(h.path)"
                :class="[ 'flex-1 text-left rounded-md overflow-hidden', collapsed ? 'py-3 justify-center' : 'px-3 py-2', isActive(h.path) ? 'bg-white font-bold' : 'hover:bg-white/60' ]"
              >
                <component is="BarChart3Icon" class="w-5 h-5 text-gray-600 flex-shrink-0" />
                <span v-if="!collapsed" class="flex-1 text-gray-700 truncate overflow-hidden text-ellipsis whitespace-nowrap max-w-[140px]">{{ h.name }}</span>
              </Button>

              <!-- three-dot menu (hidden when collapsed) -->
              <button
                v-if="!collapsed"
                @click.stop="toggleHistoryMenu(h.id, $event)"
                class="ml-2 p-1 rounded hover:bg-gray-100 text-gray-500 history-menu-button"
                aria-haspopup="true"
                :aria-expanded="openHistoryMenuId === h.id"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path d="M6 10a2 2 0 11-4 0 2 2 0 014 0zm6 0a2 2 0 11-4 0 2 2 0 014 0zM18 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </button>
            </div>

            <!-- dropdown menu -->
            <div v-if="openHistoryMenuId === h.id" ref="menuRef" class="absolute right-0 mt-1 z-50 w-48 bg-white border rounded-md shadow-lg overflow-hidden sidebar-history-menu">
                <button @click="shareHistory(h)" class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Share</button>
                <button @click="downloadHistoryCSV(h)" class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Download CSV</button>
                <div class="border-t" />
                <button @click="deleteHistory(h)" class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50">Delete</button>
            </div>
          </div>
        </div>
      </div>
    </ScrollArea>

    <Button variant="ghost" @click="collapsed = !collapsed" :class="[ 'flex items-center gap-3 w-full text-left rounded-md px-3 py-2', collapsed ? 'justify-center' : '' ]">
      <component is="ChevronLeftIcon" :class="{ 'transform rotate-180': collapsed }" class="w-5 h-5 text-gray-600" />
      <span v-if="!collapsed" class="flex-1 text-gray-700">Collapse</span>
    </Button>
    <div class="w-full h-4" />
  </aside>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Button from './Button.vue'
import ScrollArea from './ScrollArea.vue'
import { HomeIcon, UploadIcon, UserIcon, BarChart3Icon, ChevronLeftIcon } from 'lucide-vue-next'
import { api } from '../lib/api.js'

const router = useRouter()
const route = useRoute()

const collapsed = ref(false)
const processItems = ref([])
const historyItems = ref([])



const navigationItems = [
  { icon: HomeIcon, label: 'Home', path: '/' },
  { icon: UploadIcon, label: 'Upload video', path: '/upload' }
]

const sidebarWidth = computed(() => (collapsed.value ? '64px' : '280px'))

const isActive = (path) => route.path === path

const navigate = (path) => {
  router.push(path)
}

const loadProcessItems = async () => {
  try {
    // Only load processes if user is logged in
    const userData = localStorage.getItem('trackflow_user')
    if (!userData) {
      processItems.value = []
      return
    }
    
    const processes = await api.getProcesses()
    processItems.value = processes
      .filter(p => p.status === 'processing')
      .map(p => ({
        id: p.id,
        name: p.name,
        path: `/process/${p.id}`,
        status: p.status
      }))
  } catch (e) {
    console.error('Error loading process items:', e)
    processItems.value = []
  }
}

 

const handleStorageChange = (e) => {
  // Not needed anymore with API
}

const loadHistoryItems = async () => {
  try {
    // Only load history if user is logged in
    const userData = localStorage.getItem('trackflow_user')
    if (!userData) {
      historyItems.value = []
      return
    }
    
    console.log('Loading history items...')
    const history = await api.getHistory()
    console.log('History data received:', history)
    historyItems.value = history.map(h => ({
      id: h.id,
      name: h.name,
      path: `/process/${h.process_id}`,
      totalVehicles: h.total_vehicles,
      process_id: h.process_id,
      results: null // Will be fetched from process API when needed
    }))
    console.log('Processed history items:', historyItems.value)
  } catch (e) {
    console.error('Error loading history items:', e)
    historyItems.value = []
  }
}

// history menu state & handlers
const openHistoryMenuId = ref(null)
const menuRef = ref(null)

const toggleHistoryMenu = (id, e) => {
  openHistoryMenuId.value = openHistoryMenuId.value === id ? null : id
}

const closeHistoryMenu = () => {
  openHistoryMenuId.value = null
}

const onDocumentClick = (e) => {
  // If click is inside a menu or on a menu button, ignore
  const el = e.target
  if (el.closest && (el.closest('.sidebar-history-menu') || el.closest('.history-menu-button'))) {
    return
  }
  closeHistoryMenu()
}

const shareHistory = async (h) => {
  const url = `${location.origin}${h.path}`
  try {
    if (navigator.share) {
      await navigator.share({ title: h.name, text: h.name, url })
    } else if (navigator.clipboard) {
      await navigator.clipboard.writeText(url)
      alert('Link copied to clipboard')
    } else {
      window.prompt('Copy this link', url)
    }
  } catch (err) {
    console.error('Share failed', err)
  }
  closeHistoryMenu()
}

const buildCSVFromResults = (name, results) => {
  const safeName = (name || 'traffic_data').replace(/\.[^/.]+$/, '')
  const filename = `${safeName}_per_minute.csv`
  let csv = 'Menit,Kendaraan Terdeteksi'
  const hasCrossed = results?.vehicles_crossed_line !== null && results?.vehicles_crossed_line !== undefined
  if (hasCrossed) csv += ',Melewati Garis'
  csv += '\n'

  const series = results?.time_series || []
  series.forEach(item => {
    csv += `${item.minute},${item.vehicles}`
    if (hasCrossed) csv += `,${item.crossed || 0}`
    csv += '\n'
  })

  csv += '\nRingkasan\n'
  csv += `Total Kendaraan,${results?.unique_vehicles ?? 0}\n`
  if (hasCrossed) csv += `Total Melewati Garis,${results?.vehicles_crossed_line ?? 0}\n`
  if (results?.avg_vehicles_per_minute !== undefined) csv += `Rata-rata per Menit (Semua),${results.avg_vehicles_per_minute}\n`
  if (results?.density_level) csv += `Tingkat Kepadatan (Semua),${results.density_level}\n`
  if (results?.density_percentage !== undefined) csv += `Persentase Kepadatan (Semua),${results.density_percentage}%\n`
  if (results?.avg_crossed_per_minute !== undefined && results?.crossed_density_level && results?.crossed_density_percentage !== undefined) {
    csv += `Rata-rata per Menit (Melewati Garis),${results.avg_crossed_per_minute}\n`
    csv += `Tingkat Kepadatan (Melewati Garis),${results.crossed_density_level}\n`
    csv += `Persentase Kepadatan (Melewati Garis),${results.crossed_density_percentage}%\n`
  }

  return { filename, csv }
}

const downloadHistoryCSV = async (h) => {
  // If results missing or incomplete, fetch full process details
  let results = h.results
  if (!results || !results.time_series) {
    try {
      const processData = await api.getProcess(h.process_id)
      results = processData.results || processData.results || processData.statistics || processData.results || processData.results
    } catch (e) {
      console.error('Failed fetch process for CSV:', e)
    }
  }
  const { filename, csv } = buildCSVFromResults(h.name, results)
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  closeHistoryMenu()
}

const deleteHistory = async (h) => {
  const ok = confirm(`Hapus history "${h.name}" ?`)
  if (!ok) return
  try {
    await api.deleteHistory(h.id)
    loadHistoryItems()
  } catch (err) {
    console.error(err)
  }
  closeHistoryMenu()
}

let refreshInterval = null

onMounted(() => {
  console.log('Sidebar mounted, loading items...')
  loadProcessItems()
  loadHistoryItems()
  document.addEventListener('click', onDocumentClick)
  
  // Refresh every 2 seconds to catch updates
  refreshInterval = setInterval(() => {
    loadProcessItems()
    loadHistoryItems()
  }, 2000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  document.removeEventListener('click', onDocumentClick)
})
</script>
