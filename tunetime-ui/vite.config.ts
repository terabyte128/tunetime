import { defineConfig } from 'vite';
import basicSsl from '@vitejs/plugin-basic-ssl';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react(), basicSsl()],
    server: {
        proxy: {
            '/api': {
                target: 'http://localhost:5555',
                followRedirects: true,
                changeOrigin: true,
            },
            '/oauth': {
                target: 'http://localhost:5555',
            },
        },
    },
});
