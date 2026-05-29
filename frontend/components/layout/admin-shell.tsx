import {
  BarChart3,
  Building2,
  ClipboardList,
  FileText,
  Home,
  Moon,
  Receipt,
  Search,
  Settings,
  UserRound,
  WalletCards,
} from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: BarChart3 },
  { href: "/buildings", label: "Quản lý nhà", icon: Building2 },
  { href: "/rooms", label: "Phòng", icon: Home },
  { href: "/tenants", label: "Người thuê", icon: UserRound },
  { href: "/contracts", label: "Hợp đồng", icon: ClipboardList },
  { href: "/invoices", label: "Hóa đơn", icon: Receipt },
  { href: "/payments", label: "Thanh toán", icon: WalletCards },
  { href: "/expenses", label: "Thu chi", icon: FileText },
];

export function AdminShell({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="min-h-screen bg-stone-50">
      <aside className="fixed inset-y-0 left-0 hidden w-72 border-r border-border bg-white lg:flex lg:flex-col">
        <div className="flex h-20 items-center gap-3 px-6">
          <div className="flex size-11 items-center justify-center rounded-lg bg-ink text-white">
            <Building2 className="size-5" />
          </div>
          <div>
            <p className="font-semibold text-ink">NhàTrọ Pro</p>
            <p className="text-sm text-slate-500">Quản lý cho thuê</p>
          </div>
        </div>
        <nav className="flex-1 space-y-1 px-3">
          {navItems.map((item) => (
            <Link
              className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-slate-700 hover:bg-muted hover:text-ink"
              href={item.href}
              key={item.href}
            >
              <item.icon className="size-4" />
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="border-t border-border p-4">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-full bg-emerald-100 text-emerald-700">
              <UserRound className="size-5" />
            </div>
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-ink">Chủ đầu tư</p>
              <p className="truncate text-xs text-slate-500">Admin</p>
            </div>
          </div>
        </div>
      </aside>
      <div className="lg:pl-72">
        <header className="sticky top-0 z-10 flex h-20 items-center justify-between border-b border-border bg-white px-4 lg:px-8">
          <div className="relative hidden w-full max-w-sm md:block">
            <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400" />
            <input
              className="h-11 w-full rounded-lg border border-border bg-white pl-10 pr-3 text-sm outline-none focus:border-slate-400"
              placeholder="Tìm phòng, người thuê..."
            />
          </div>
          <div className="ml-auto flex items-center gap-2">
            <Button aria-label="Đổi giao diện" title="Đổi giao diện" type="button" variant="ghost">
              <Moon className="size-5" />
            </Button>
            <Button aria-label="Cài đặt" title="Cài đặt" type="button" variant="ghost">
              <Settings className="size-5" />
            </Button>
          </div>
        </header>
        <main className="px-4 py-8 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
