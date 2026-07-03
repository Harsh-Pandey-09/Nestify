import { NavLink } from "react-router-dom";

export default function Sidebar({ title, links }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-title">{title}</div>
      {links.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          end={link.end}
          className={({ isActive }) =>
            isActive ? "sidebar-link active" : "sidebar-link"
          }
        >
          {link.label}
        </NavLink>
      ))}
    </aside>
  );
}
