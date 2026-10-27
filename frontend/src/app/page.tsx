
"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { dashboardApi, ticketsApi } from "@/lib/api";
import type { ServiceTicket, DashboardMetrics } from "@/types";

// ── Helpers ───────────────────────────────────────────────────────────────────
function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function StatusBadge({ status }: { status: string }) {
  const s = status.toLowerCase();
  const map: Record<string, string> = {
    new: "bg-sky-100 text-sky-700",
    assigned: "bg-blue-100 text-blue-700",
    in_progress: "bg-amber-100 text-amber-700",
    waiting_customer: "bg-emerald-100 text-teal-800",
    resolved: "bg-green-100 text-green-700",
    closed: "bg-gray-100 text-gray-500",
  };
  const cls = map[s] ?? "bg-gray-100 text-gray-600";
  const labels: Record<string, string> = {
    new: "New",
    assigned: "Assigned",
    in_progress: "In Progress",
    waiting_customer: "Waiting",
    resolved: "Resolved",
    closed: "Closed",
  };
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${cls}`}>
      {labels[s] ?? s}
    </span>
  );
}

function PriorityDot({ priority }: { priority: string }) {
  const colors: Record<string, string> = {
    critical: "#ef4444",
    high: "#f97316",
    medium: "#f59e0b",
    low: "#22c55e",
  };
  return (
    <span className="flex items-center gap-1.5">
      <span
        style={{ backgroundColor: colors[priority.toLowerCase()] ?? "#9ca3af" }}
        className="inline-block h-2 w-2 rounded-full"
      />
      <span className="text-xs text-gray-600 capitalize">{priority}</span>
    </span>
  );
}

// ── Static nav / tab data ─────────────────────────────────────────────────────
const NAV_ITEMS = [
  { label: "Dashboard", badge: null, active: false, icon: "⊞" },
  { label: "Service Desk", badge: null, active: true, icon: "🎫" },
  { label: "Assets", badge: null, active: false, icon: "📦" },
  { label: "Knowledge Base", badge: null, active: false, icon: "📖" },
  { label: "Maintenance", badge: null, active: false, icon: "🔧" },
  { label: "Reports", badge: null, active: false, icon: "📊" },
  { label: "Settings", badge: null, active: false, icon: "⚙" },
];

const TABS = ["All", "New", "In Progress", "Resolved", "Critical"];

const TAB_FILTERS: Record<string, Partial<ServiceTicket>> = {
  New: { status: "new" },
  "In Progress": { status: "in_progress" },
  Resolved: { status: "resolved" },
  Critical: { priority: "critical" },
};

// ── Main component ─────────────────────────────────────────────────────────────
export default function HomePage() {
  const { user, isLoading: authLoading, logout } = useAuth();
  const router = useRouter();

  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [tickets, setTickets] = useState<ServiceTicket[]>([]);
  const [dataStatus, setDataStatus] = useState<"loading" | "ok" | "error" | "unauth">("loading");
  const [activeTab, setActiveTab] = useState(0);
  const [search, setSearch] = useState("");

  // Redirect unauthenticated users to login
  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/login");
    }
  }, [authLoading, user, router]);

  const loadData = useCallback(async () => {
    if (!user) return;
    setDataStatus("loading");
    try {
      const [dashRes, tickRes] = await Promise.all([
        dashboardApi.metrics(),
        ticketsApi.list({ limit: 25, skip: 0 }),
      ]);
      setMetrics(dashRes.data);
      // Backend returns a plain array — not wrapped in { items }
      setTickets(Array.isArray(tickRes.data) ? tickRes.data : []);
      setDataStatus("ok");
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      if (status === 401 || status === 403) {
        setDataStatus("unauth");
      } else {
        setDataStatus("error");
      }
    }
  }, [user]);

  useEffect(() => {
    if (user) void loadData();
  }, [user, loadData]);

  // Filter tickets based on tab + search
  const tabFilter = TABS[activeTab] !== "All" ? TAB_FILTERS[TABS[activeTab]] : null;
  const filtered = tickets.filter((t) => {
    if (tabFilter) {
      if ("status" in tabFilter && t.status !== tabFilter.status) return false;
      if ("priority" in tabFilter && t.priority !== tabFilter.priority) return false;
    }
    if (search) {
      const q = search.toLowerCase();
      return (
        t.title?.toLowerCase().includes(q) ||
        t.ticket_number?.toLowerCase().includes(q) ||
        t.category?.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const statCards = [
    { label: "Total Assets", value: metrics?.total_assets, color: "#0f5c5b", bg: "#effaf5", symbol: "📦" },
    { label: "Open Tickets", value: metrics?.open_tickets, color: "#2563eb", bg: "#eff6ff", symbol: "🎫" },
    { label: "Critical", value: metrics?.critical_tickets, color: "#dc2626", bg: "#fef2f2", symbol: "⚠️" },
    { label: "Overdue", value: metrics?.overdue_tickets, color: "#d97706", bg: "#fffbeb", symbol: "⏰" },
  ];

  // Loading / auth gate
  if (authLoading || (!user && dataStatus !== "error")) {
    return (
      <div className="flex h-screen items-center justify-center bg-white">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-emerald-100 border-t-teal-800" />
      </div>
    );
  }

  return (
    <div
      className="flex h-screen w-full overflow-hidden"
      style={{ background: "#f8fbfa", fontFamily: "'Inter', system-ui, sans-serif" }}
    >
      {/* ── Sidebar ─────────────────────────────────────────────────────────── */}
      <aside
        className="flex h-full flex-shrink-0 flex-col py-6"
        style={{ width: 220, background: "#ffffff", borderRight: "1px solid #e2e8f0" }}
      >
        {/* Logo */}
        <div className="px-5 mb-7">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg text-white text-sm font-bold" style={{ background: "#0f5c5b" }}>
              F
            </div>
            <div>
              <p className="text-sm font-bold leading-tight" style={{ color: "#111827" }}>FieldOps</p>
              <p className="text-[10px] font-semibold uppercase tracking-wide" style={{ color: "#9ca3af" }}>service desk</p>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 space-y-0.5 px-3">
          {NAV_ITEMS.map(({ label, badge, active, icon }) => (
            <button
              key={label}
              className="group flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-150"
              style={active ? { background: "#0f5c5b", color: "#fff", boxShadow: "0 4px 12px rgba(15,92,91,0.16)" } : { color: "#64748b" }}
              onMouseEnter={(e) => { if (!active) { (e.currentTarget as HTMLButtonElement).style.background = "#f3f4f6"; (e.currentTarget as HTMLButtonElement).style.color = "#111827"; } }}
              onMouseLeave={(e) => { if (!active) { (e.currentTarget as HTMLButtonElement).style.background = "transparent"; (e.currentTarget as HTMLButtonElement).style.color = "#6b7280"; } }}
            >
              <span className="flex items-center gap-3"><span className="text-base">{icon}</span>{label}</span>
              {badge !== null && (
                <span className="flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold" style={active ? { background: "rgba(255,255,255,0.3)", color: "#fff" } : { background: "#effaf5", color: "#0f5c5b" }}>
                  {badge}
                </span>
              )}
            </button>
          ))}
        </nav>

        {/* Create ticket button */}
        <div className="px-3 mt-4">
          <button
            id="create-ticket-btn"
            className="flex w-full items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold text-white transition hover:opacity-90 active:scale-95"
            style={{ background: "#0f5c5b", boxShadow: "0 4px 12px rgba(15,92,91,0.16)" }}
          >
            + Create a Ticket
          </button>
        </div>

        {/* User info + logout */}
        <div className="mt-5 flex items-center gap-3 px-4 pt-5" style={{ borderTop: "1px solid #f3f4f6" }}>
          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-xs font-bold text-white" style={{ background: "linear-gradient(135deg,#a78bfa,#60a5fa)" }}>
            {user?.full_name?.slice(0, 2).toUpperCase() ?? "U"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="truncate text-xs font-semibold" style={{ color: "#111827" }}>{user?.full_name ?? "User"}</p>
            <p className="truncate text-[10px] capitalize" style={{ color: "#9ca3af" }}>{user?.role ?? ""}</p>
          </div>
          <button
            id="logout-btn"
            onClick={logout}
            title="Sign out"
            className="text-gray-400 hover:text-red-500 transition text-xs"
          >
            ⏏
          </button>
        </div>
      </aside>

      {/* ── Main card ───────────────────────────────────────────────────────── */}
      <div className="flex flex-1 flex-col overflow-hidden p-4">
        <div className="flex flex-1 flex-col overflow-hidden" style={{ background: "#fff", borderRadius: 20, boxShadow: "0 20px 60px rgba(99,60,180,0.12)" }}>

          {/* Top bar */}
          <div className="flex items-center justify-between px-6 py-3.5" style={{ borderBottom: "1px solid #f3f4f6" }}>
            {/* Tabs */}
            <div className="flex items-center gap-1">
              {TABS.map((tab, i) => (
                <button
                  key={tab}
                  id={`tab-${tab.toLowerCase().replace(/\s+/g, "-")}`}
                  onClick={() => setActiveTab(i)}
                  className="rounded-lg px-3 py-1.5 text-sm font-medium transition-all duration-150"
                  style={activeTab === i ? { color: "#111827", fontWeight: 700 } : { color: "#9ca3af" }}
                  onMouseEnter={(e) => { if (activeTab !== i) (e.currentTarget as HTMLButtonElement).style.color = "#374151"; }}
                  onMouseLeave={(e) => { if (activeTab !== i) (e.currentTarget as HTMLButtonElement).style.color = "#9ca3af"; }}
                >
                  {tab}
                </button>
              ))}
            </div>

            {/* Search + API status */}
            <div className="flex items-center gap-3">
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-xs">🔍</span>
                <input
                  id="tickets-search"
                  type="text"
                  placeholder="Search tickets…"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="h-8 w-48 rounded-lg bg-gray-50 pl-8 pr-3 text-sm text-gray-700 placeholder:text-gray-400 transition"
                  style={{ border: "1px solid #e5e7eb", outline: "none" }}
                  onFocus={(e) => { (e.currentTarget as HTMLInputElement).style.borderColor = "#54cfa0"; (e.currentTarget as HTMLInputElement).style.background = "#fff"; }}
                  onBlur={(e) => { (e.currentTarget as HTMLInputElement).style.borderColor = "#e5e7eb"; (e.currentTarget as HTMLInputElement).style.background = "#f9fafb"; }}
                />
              </div>
              <button
                id="refresh-btn"
                onClick={() => void loadData()}
                title="Refresh"
                className="rounded-lg px-2 py-1 text-xs text-gray-400 transition hover:text-teal-800 hover:bg-emerald-50"
                style={{ border: "1px solid #e5e7eb" }}
              >
                ↺
              </button>
              <div
                id="api-status-indicator"
                className="flex items-center gap-1.5 rounded-full px-3 py-1 text-xs"
                style={{
                  border: "1px solid #e5e7eb",
                  background: "#f9fafb",
                  color: dataStatus === "ok" ? "#15803d" : dataStatus === "loading" ? "#92400e" : "#b91c1c",
                }}
              >
                <span>{dataStatus === "loading" ? "⏳" : dataStatus === "ok" ? "✅" : "❌"}</span>
                {dataStatus === "loading" ? "Loading" : dataStatus === "ok" ? "Live" : dataStatus === "unauth" ? "Auth error" : "Offline"}
              </div>
            </div>
          </div>

          {/* Error banners */}
          {dataStatus === "unauth" && (
            <div className="mx-6 mt-4 rounded-lg px-4 py-3 text-sm" style={{ background: "#fef2f2", border: "1px solid #fecaca", color: "#991b1b" }}>
              Session expired or insufficient permissions.{" "}
              <button className="font-semibold underline" onClick={logout}>Sign in again</button>
            </div>
          )}
          {dataStatus === "error" && (
            <div className="mx-6 mt-4 rounded-lg px-4 py-3 text-sm" style={{ background: "#fffbeb", border: "1px solid #fde68a", color: "#92400e" }}>
              Could not reach the backend. Verify the API server is running at{" "}
              <code className="font-mono">{process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000"}</code>.{" "}
              <button className="font-semibold underline" onClick={() => void loadData()}>Retry</button>
            </div>
          )}

          {/* Scrollable content */}
          <div className="flex flex-1 flex-col overflow-y-auto px-6 py-5">

            {/* Section header */}
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h1 className="text-lg font-bold" style={{ color: "#111827" }}>Service Tickets</h1>
                <p className="text-xs mt-0.5" style={{ color: "#9ca3af" }}>
                  {dataStatus === "ok" ? `${filtered.length} records` : "—"} · IT &amp; Security Field Operations
                </p>
              </div>
              <button
                id="export-csv-btn"
                className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-medium transition"
                style={{ border: "1px solid #e5e7eb", color: "#374151", background: "#fff", boxShadow: "0 1px 3px rgba(0,0,0,0.06)" }}
                onMouseEnter={(e) => ((e.currentTarget as HTMLButtonElement).style.background = "#f9fafb")}
                onMouseLeave={(e) => ((e.currentTarget as HTMLButtonElement).style.background = "#fff")}
              >
                ↓ Export CSV
              </button>
            </div>

            {/* Tickets table */}
            <div className="overflow-hidden" style={{ borderRadius: 12, border: "1px solid #f3f4f6", boxShadow: "0 1px 4px rgba(0,0,0,0.04)" }}>
              <table id="tickets-table" className="w-full" style={{ minWidth: 700 }}>
                <thead>
                  <tr style={{ background: "#fafafa", borderBottom: "1px solid #f3f4f6" }}>
                    {["Ticket #", "Date ▼", "Title", "Category", "Status", "Priority"].map((h) => (
                      <th key={h} className="px-4 py-3 text-left" style={{ fontSize: 11, fontWeight: 600, color: "#9ca3af", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {dataStatus === "loading" ? (
                    <tr>
                      <td colSpan={6} className="py-12 text-center text-sm" style={{ color: "#9ca3af" }}>
                        <span className="inline-block h-5 w-5 animate-spin rounded-full border-2 border-emerald-200 border-t-teal-800 mr-2 align-middle" />
                        Loading tickets…
                      </td>
                    </tr>
                  ) : dataStatus !== "ok" ? (
                    <tr>
                      <td colSpan={6} className="py-12 text-center text-sm" style={{ color: "#9ca3af" }}>
                        {dataStatus === "unauth"
                          ? "Authentication required — please sign in."
                          : "Backend unavailable — check server logs."}
                      </td>
                    </tr>
                  ) : filtered.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-12 text-center text-sm" style={{ color: "#9ca3af" }}>
                        No tickets match the current filter.
                      </td>
                    </tr>
                  ) : (
                    filtered.map((t) => (
                      <tr
                        key={t.id}
                        className="ticket-row"
                        style={{ borderBottom: "1px solid #fafafa", cursor: "pointer", transition: "background 0.1s" }}
                        onMouseEnter={(e) => ((e.currentTarget as HTMLTableRowElement).style.background = "#faf5ff")}
                        onMouseLeave={(e) => ((e.currentTarget as HTMLTableRowElement).style.background = "transparent")}
                      >
                        <td className="px-4 py-3" style={{ fontFamily: "monospace", fontSize: 12, color: "#6b7280", fontWeight: 600 }}>
                          {t.ticket_number}
                        </td>
                        <td className="px-4 py-3" style={{ fontSize: 12, color: "#6b7280", whiteSpace: "nowrap" }}>
                          {timeAgo(t.created_at)}
                        </td>
                        <td className="px-4 py-3" style={{ fontSize: 13, fontWeight: 500, color: "#111827", maxWidth: 240, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {t.title}
                        </td>
                        <td className="px-4 py-3" style={{ fontSize: 12, color: "#6b7280", textTransform: "capitalize" }}>
                          {t.category?.replace(/_/g, " ") ?? "—"}
                        </td>
                        <td className="px-4 py-3">
                          <StatusBadge status={t.status} />
                        </td>
                        <td className="px-4 py-3">
                          <PriorityDot priority={t.priority} />
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Summary stat cards */}
            <div className="mt-5 grid gap-4" style={{ gridTemplateColumns: "repeat(4, 1fr)" }}>
              {statCards.map(({ label, value, color, bg, symbol }) => (
                <div
                  key={label}
                  className="flex items-center gap-4 rounded-xl p-4"
                  style={{ border: "1px solid #f3f4f6", background: "#fff", boxShadow: "0 1px 4px rgba(0,0,0,0.04)" }}
                >
                  <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl text-lg" style={{ background: bg }}>
                    {symbol}
                  </div>
                  <div>
                    <p className="text-xs font-medium" style={{ color: "#9ca3af" }}>{label}</p>
                    <p className="mt-0.5 text-2xl font-bold leading-none" style={{ color }}>
                      {dataStatus === "loading" ? (
                        <span style={{ color: "#e5e7eb" }}>—</span>
                      ) : value !== undefined ? (
                        value
                      ) : (
                        <span style={{ color: "#d1d5db" }}>—</span>
                      )}
                    </p>
                  </div>
                </div>
              ))}
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
