import { createApp } from 'vue';
import { createPinia } from 'pinia';

import { router } from './app/router';
import AppShell from './layouts/AppShell.vue';
import '../../../desktop_app/assets/css/variables.css';
import '../../../desktop_app/assets/css/shell.css';
import '../../../desktop_app/assets/css/components.css';
import '../../../desktop_app/assets/css/interactions.css';
import './styles/main.css';
import './styles/copywriter.css';
import './styles/ai-content-factory.css';
import './styles/creative-workshop.css';
import './styles/data-collector.css';
import './styles/scheduled-publish.css';
import './styles/video-editor.css';

const app = createApp(AppShell);

app.use(createPinia());
app.use(router);
app.mount('#app');
