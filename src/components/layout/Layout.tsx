import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';

export default function Layout() {
  return (
    <div className="min-h-screen bg-dark-bg">
      <Navbar />
      <main className="pt-20 pb-12">
        <Outlet />
      </main>
      <footer className="border-t border-dark-border py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-500 text-sm">
          <p>&copy; 2024 SkillVerify. Verifiziere deine Skills.</p>
        </div>
      </footer>
    </div>
  );
}
