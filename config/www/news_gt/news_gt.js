class NewsCard extends HTMLElement {
    setConfig(config) {
      this.config = config;
    }
  
    set hass(hass) {
      const entityId = this.config.entity;
      const state = hass.states[entityId];
      const articles = state.attributes.articles || [];
  
      this.innerHTML = `
        <ha-card>
          <style>
            ha-card {
            border-radius: 16px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            font-family: Arial, sans-serif;
            max-width: 400px;
            }

            .card-content {
            margin-top: 12px;
            }

            .article {
            display: block;
            margin-bottom: 35px;
            border-radius: 12px;
            }

            .thumbnail {
            width: 100%;
            height: 60px;
            border-radius: 12px;
            overflow: hidden;
            flex-shrink: 0;
            }

            .thumbnail img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            }

            .text-content h3 {
            margin: 0;
            font-size: 16px;
            font-weight: bold;
            }

            .text-content h3 a {
            text-decoration: none;
            color: inherit;
            }

            .text-content p {
            font-size: 14px;
            margin: 0px;
            color: #888;
            }
          </style>
          <div class="card-content">
            ${articles.map(article => `
              <div class="article">
                ${article.thumbnail ? `<div class="thumbnail"><img src="${article.thumbnail}" alt="${article.title}"></div>` : ''}
                <div class="text-content">
                    <h3><a href="${article.link}" target="_blank">${article.title}</a></h3>
                    <div class="published">${article.published}</div>
                    <p>${article.summary}</p>
                </div>
              </div>
            `).join('')}
          </div>
        </ha-card>
      `;
    }
  
    getCardSize() {
        return 3;
    }

    static getConfigElement() {
        return document.createElement('news-card-editor');
    }
    
    static getStubConfig() {
        return { entity: 'sensor.latest_news' };
    }
}

class NewsCardEditor extends HTMLElement {
    setConfig(config) {
      this.config = config;
      this.render();
    }
  
    connectedCallback() {
      this.render();
    }
  
    render() {
      if (!this.config) {
        this.innerHTML = `<div class="card-config">Loading...</div>`;
        return;
      }
  
      this.innerHTML = `
        <div class="card-config">
          <paper-input label="Entity" value="${this.config.entity || 'sensor.latest_news'}" config-path="entity"></paper-input>
        </div>
      `;
    }
  }
  
customElements.define('news-card', NewsCard);
customElements.define('news-card-editor', NewsCardEditor);
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'news-card',
  name: 'News Card',
  description: 'Displays news articles from a sensor',
});