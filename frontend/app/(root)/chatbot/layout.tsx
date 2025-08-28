import Sidebarprovider from "./sidebar-provide";

export default function ChatbotLayout({ children }: { children: React.ReactNode }) {
  return <Sidebarprovider>{children}</Sidebarprovider>;
}
