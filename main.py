import os
import psutil
import shutil
import threading
import webview  # Ensure you ran: pip install pywebview
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="StorageOS Pro")

# --- BACKEND LOGIC ---
def get_size(bytes):
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < 1024: return f"{bytes:.2f}{unit}B"
        bytes /= 1024

def get_dir_size(path):
    total = 0
    try:
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file(): total += entry.stat().st_size
                elif entry.is_dir() and not entry.is_symlink(): 
                    total += get_dir_size(entry.path)
    except (PermissionError, FileNotFoundError): pass
    return total

def auto_detect_junk(base_path, max_depth=2):
    found = []
    junk_map = {
        'cache': 'Temporary application data. Deleting this is safe; apps will recreate what they need.',
        'tmp': 'Temporary system files. Safe to delete as they are not needed for long-term operation.',
        'temp': 'Temporary storage. Safe to delete.',
        'logs': 'Records of system events. Safe to delete; the system will start writing new logs.',
        '__pycache__': 'Compiled Python files. Python will regenerate them automatically.'
    }
    
    try:
        for root, dirs, files in os.walk(base_path):
            depth = root.count(os.sep) - base_path.count(os.sep)
            if depth >= max_depth:
                del dirs[:] 
                continue

            for d in dirs:
                for key, desc in junk_map.items():
                    if key in d.lower():
                        full_path = os.path.join(root, d)
                        size = get_dir_size(full_path)
                        if size > 1024 * 1024: 
                            found.append({
                                "name": f"Detected {d.title()}",
                                "path": full_path,
                                "bytes": size,
                                "size": get_size(size),
                                "description": desc
                            })
                            break

            for f in files:
                if f.endswith(('.log', '.gz', '.bak', '.old')):
                    fp = os.path.join(root, f)
                    try:
                        f_size = os.path.getsize(fp)
                        if f_size > 50 * 1024 * 1024: 
                            found.append({
                                "name": f"Large {f.split('.')[-1].upper()} File",
                                "path": fp,
                                "bytes": f_size,
                                "size": get_size(f_size),
                                "description": "Large log or backup file. Deleting will free up space immediately."
                            })
                    except: continue
    except: pass
    return found

@app.get("/api/usage")
async def disk_usage():
    results = []
    for p in psutil.disk_partitions():
        if 'loop' in p.device or p.fstype in ['squashfs', 'tmpfs']: continue
        try:
            u = psutil.disk_usage(p.mountpoint)
            results.append({
                "device": p.device, "mount": p.mountpoint, "total": get_size(u.total),
                "used": get_size(u.used), "percent": u.percent,
                "status": "CRITICAL" if u.percent > 90 else "OK"
            })
        except: continue
    return results

@app.get("/api/analysis")
async def analyze_disk(path: str = "/"):
    folder_sizes = []
    try:
        for entry in os.scandir(path):
            if entry.is_dir() and not entry.is_symlink():
                size = get_dir_size(entry.path)
                folder_sizes.append({"folder": entry.path, "bytes": size, "size": get_size(size)})
    except: return {"error": "Access Denied"}
    folder_sizes.sort(key=lambda x: x["bytes"], reverse=True)
    return folder_sizes[:10]

@app.get("/api/suggestions")
async def get_suggestions():
    system_junk = auto_detect_junk("/", max_depth=2)
    user_junk = auto_detect_junk(os.path.expanduser("~"), max_depth=2)
    all_junk = {item['path']: item for item in (system_junk + user_junk)}.values()
    return sorted(list(all_junk), key=lambda x: x['bytes'], reverse=True)

@app.post("/api/delete")
async def delete_path(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Path not found")
    try:
        if os.path.isfile(path): os.remove(path)
        else: shutil.rmtree(path)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <title>StorageOS</title>
        <style>
            ::-webkit-scrollbar { width: 8px; }
            ::-webkit-scrollbar-track { background: #000; }
            ::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }
        </style>
    </head>
    <body class="bg-black text-gray-100 flex h-screen overflow-hidden font-sans">
        <aside class="w-64 bg-gray-900 border-r border-gray-800 p-6 flex flex-col">
            <h1 class="text-2xl font-black text-blue-500 mb-10 tracking-tighter italic">STORAGE<span class="text-white">OS</span></h1>
            <nav class="space-y-4">
                <button onclick="loadDashboard()" class="w-full text-left flex items-center p-2 hover:text-blue-400 transition font-bold uppercase text-xs tracking-widest"><i class="fas fa-th-large mr-3"></i> Dashboard</button>
                <button onclick="loadAnalysis('/')" class="w-full text-left flex items-center p-2 hover:text-blue-400 transition font-bold uppercase text-xs tracking-widest"><i class="fas fa-search mr-3"></i> Analysis</button>
                <button onclick="loadSuggestions()" class="w-full text-left flex items-center p-2 hover:text-blue-400 transition font-bold uppercase text-xs tracking-widest"><i class="fas fa-magic mr-3"></i> Suggestions</button>
            </nav>
        </aside>

        <main id="content" class="flex-1 p-10 overflow-y-auto bg-gray-950"></main>

        <script>
            const content = document.getElementById('content');

            async function loadDashboard() {
                const res = await fetch('/api/usage');
                const data = await res.json();
                let html = '<h2 class="text-4xl font-bold mb-8 text-white">System Health</h2><div class="grid grid-cols-1 xl:grid-cols-2 gap-6">';
                data.forEach(d => {
                    const barColor = d.percent > 90 ? 'bg-red-500' : 'bg-blue-500';
                    html += `<div class="bg-gray-900 border border-gray-800 p-6 rounded-2xl shadow-xl">
                        <div class="flex justify-between items-center mb-4 text-gray-500">
                            <span class="text-xs font-bold uppercase font-mono tracking-widest">${d.device}</span>
                            <span class="px-2 py-1 rounded text-xs font-bold ${d.status === 'OK' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300 animate-pulse'}">${d.status}</span>
                        </div>
                        <div class="text-3xl font-bold mb-2 text-white">${d.mount}</div>
                        <div class="h-3 w-full bg-gray-800 rounded-full mb-3 overflow-hidden">
                            <div class="h-full ${barColor}" style="width:${d.percent}%"></div>
                        </div>
                        <div class="flex justify-between text-sm text-gray-400 font-medium">
                            <span>Used: ${d.used}</span>
                            <span>${d.percent}% Capacity</span>
                        </div>
                    </div>`;
                });
                content.innerHTML = html + '</div>';
            }

            async function loadSuggestions() {
                content.innerHTML = '<div class="h-full flex flex-col items-center justify-center animate-pulse"><i class="fas fa-broom text-4xl mb-4 text-green-500"></i><div class="text-xl">Detecting Safe-to-Delete Junk...</div></div>';
                const res = await fetch('/api/suggestions');
                const data = await res.json();
                let html = '<h2 class="text-4xl font-bold mb-2 text-white">Safe Cleanup</h2><p class="mb-8 text-gray-500">Items that can be deleted without impacting your system.</p><div class="grid grid-cols-1 gap-4">';
                data.forEach(s => {
                    html += `<div class="bg-gray-900 border border-gray-800 p-6 rounded-2xl hover:border-blue-900 transition shadow-lg">
                        <div class="flex justify-between items-start mb-4">
                            <div class="flex items-center">
                                <div class="bg-blue-900/20 p-3 rounded-lg mr-4 text-blue-400"><i class="fas fa-info-circle"></i></div>
                                <div>
                                    <div class="font-bold text-xl text-white">${s.name}</div>
                                    <div class="text-xs text-gray-500 font-mono mt-1">${s.path}</div>
                                </div>
                            </div>
                            <div class="text-right">
                                <div class="text-2xl font-black text-white">${s.size}</div>
                            </div>
                        </div>
                        <div class="text-sm text-gray-400 bg-black/30 p-3 rounded-xl mb-4 border border-gray-800/50 italic font-mono">
                            ${s.description}
                        </div>
                        <div class="flex justify-end">
                            <button onclick="confirmDelete('${s.path}')" class="bg-red-600 hover:bg-red-700 text-white text-[10px] font-black px-6 py-2 rounded-lg transition uppercase tracking-widest shadow-lg shadow-red-900/20">
                                Delete Permanently
                            </button>
                        </div>
                    </div>`;
                });
                if(data.length === 0) html += '<p class="text-center text-gray-500 italic">No safe junk detected at this scan depth.</p>';
                content.innerHTML = html + '</div>';
            }

            async function confirmDelete(path) {
                if(confirm("Are you sure? This action cannot be undone.")) {
                    const res = await fetch(`/api/delete?path=${encodeURIComponent(path)}`, { method: 'POST' });
                    if(res.ok) {
                        loadSuggestions();
                        loadDashboard();
                    } else {
                        alert("Permission denied. Try running as sudo.");
                    }
                }
            }
            
            async function loadAnalysis(path) {
                content.innerHTML = '<div class="h-full flex flex-col items-center justify-center animate-pulse"><i class="fas fa-spinner fa-spin text-4xl mb-4 text-blue-500"></i><div class="text-xl">Calculating sizes...</div></div>';
                const res = await fetch(`/api/analysis?path=${path}`);
                const data = await res.json();
                let html = `<h2 class="text-4xl font-bold mb-8 text-white">Analysis: <span class="text-gray-500 font-mono">${path}</span></h2><div class="bg-gray-900 rounded-2xl border border-gray-800 overflow-hidden shadow-2xl">`;
                html += '<table class="w-full text-left text-sm text-gray-400 font-mono"><tr class="border-b border-gray-800 uppercase tracking-widest text-[10px] font-black bg-gray-900"><th class="p-4">Directory</th><th class="p-4 text-right">Size</th><th class="p-4"></th></tr>';
                data.forEach(f => {
                    html += `<tr class="border-b border-gray-800 hover:bg-gray-850 transition text-gray-300">
                        <td class="p-4 truncate max-w-xs">${f.folder}</td>
                        <td class="p-4 text-right font-bold text-blue-400 font-sans">${f.size}</td>
                        <td class="p-4 text-right"><button onclick="loadAnalysis('${f.folder}')" class="bg-gray-800 px-4 py-1 rounded hover:bg-blue-600 text-[10px] font-black uppercase transition">Explore</button></td>
                    </tr>`;
                });
                content.innerHTML = html + '</table></div>';
            }

            loadDashboard();
        </script>
    </body>
    </html>
    """

# --- SYSTEM BUNDLING LOGIC ---
def run_server():
    """Start the backend in its own thread."""
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

if __name__ == "__main__":
    # 1. Spin up the FastAPI server in the background
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # 2. Open the UI in a dedicated Desktop Window (No browser URL bar)
    webview.create_window(
        'StorageOS Pro', 
        'http://127.0.0.1:8000',
        width=1280,
        height=850,
        resizable=True,
        background_color='#000000'
    )
    webview.start()