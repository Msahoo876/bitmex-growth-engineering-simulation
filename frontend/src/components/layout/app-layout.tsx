import {
  BarChart3,
  Bot,
  Gauge,
  GitBranch,
  LayoutDashboard,
  PieChart
} from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

import { cn } from "../../lib/cn";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/funnels", label: "Funnels", icon: GitBranch },
  { to: "/attribution", label: "Attribution", icon: PieChart },
  { to: "/quality", label: "Data Quality", icon: Gauge },
  { to: "/insights", label: "AI Insights", icon: Bot }
];

export function AppLayout() {
  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[260px_1fr]">
      <aside className="border-b border-border bg-black/70 backdrop-blur lg:min-h-screen lg:border-b-0 lg:border-r">
        <div className="flex h-16 items-center gap-3 px-5">
          <div className="grid h-9 w-9 place-items-center rounded-md bg-primary font-black text-black">
            X
          </div>
          <div>
            <p className="text-sm font-semibold text-white">BitMEX Growth</p>
            <p className="text-xs text-muted">Engineering Simulation</p>
          </div>
        </div>
        <nav className="flex gap-2 overflow-x-auto px-3 pb-3 lg:block lg:space-y-1 lg:overflow-visible lg:pb-0">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                cn(
                  "flex min-w-fit items-center gap-3 rounded-md px-3 py-2.5 text-sm text-zinc-400 transition hover:bg-zinc-900 hover:text-white",
                  isActive && "bg-primary/10 text-primary"
                )
              }
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="min-w-0 px-4 py-5 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}
