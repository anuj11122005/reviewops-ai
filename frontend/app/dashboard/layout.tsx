import Link from "next/link";
import { LayoutDashboard, Activity, MessageSquare } from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-64 bg-white border-r border-gray-200">
        <div className="h-full px-3 py-4 overflow-y-auto">
          <ul className="space-y-2 font-medium">
            <li>
              <Link
                href="/dashboard/status"
                className="flex items-center p-2 text-gray-900 rounded-lg hover:bg-gray-100"
              >
                <LayoutDashboard className="w-5 h-5 text-gray-500" />
                <span className="ml-3">Agent Status</span>
              </Link>
            </li>
            <li>
              <Link
                href="/models"
                className="flex items-center p-2 text-gray-900 rounded-lg hover:bg-gray-100"
              >
                <Activity className="w-5 h-5 text-gray-500" />
                <span className="ml-3">Model Registry</span>
              </Link>
            </li>
            <li>
              <Link
                href="/monitoring"
                className="flex items-center p-2 text-gray-900 rounded-lg hover:bg-gray-100"
              >
                <Activity className="w-5 h-5 text-gray-500" />
                <span className="ml-3">Monitoring</span>
              </Link>
            </li>
            <li>
              <Link
                href="/dashboard/feedback"
                className="flex items-center p-2 text-gray-900 rounded-lg hover:bg-gray-100"
              >
                <MessageSquare className="w-5 h-5 text-gray-500" />
                <span className="ml-3">Feedback</span>
              </Link>
            </li>
            <li>
              <Link
                href="/settings"
                className="flex items-center p-2 text-gray-900 rounded-lg hover:bg-gray-100"
              >
                <MessageSquare className="w-5 h-5 text-gray-500" />
                <span className="ml-3">Settings</span>
              </Link>
            </li>
          </ul>
        </div>
      </aside>
      <main className="flex-1 overflow-auto bg-gray-50">{children}</main>
    </div>
  );
}
