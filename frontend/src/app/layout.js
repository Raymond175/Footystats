import localFont from "next/font/local";
import "./globals.css";
import Footer from "./components/Footer";
import Navbar
 from "./components/Navbar";
const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata = {
  title: "Footstats",
  description: "Footstas is the ultimate football stats and data at your fingertips.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        {children}

        <Footer />
      </body>
    </html>
  );
}
