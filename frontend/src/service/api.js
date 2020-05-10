const url = process.env.VUE_APP_URL || 'http://localhost:8000/api';

const sortedApi = (path, ctx) => {
  if (ctx === undefined || ctx === null) {
    return path;
  }

  if (!ctx.hasOwnProperty('sortBy') || !ctx.hasOwnProperty('sortDesc')) {
    return path;
  }

  let { sortBy } = ctx;
  const { sortDesc } = ctx;

  if (sortDesc) {
    sortBy = `-${sortBy}`;
  }

  return `${path}&sort=${sortBy}`;
};

/**
 * Returns urls for communicating with the backend api.
 *
 */
const Api = {

  activeCompany: () => `${url}/companies/get/active/`,

  liquidityOverview: () => `${url}/companies/liquidity/`,

  companies: (page, size, ctx) => sortedApi(`${url}/companies/?page=${page}&page_size=${size}`, ctx),

  trades: (page, size, ctx) => sortedApi(`${url}/trades/?page=${page}&page_size=${size}`, ctx),

  orders: (page, size, ctx) => sortedApi(`${url}/orders/?page=${page}&page_size=${size}`, ctx),

  ordersByUser: (page, size, ctx) => sortedApi(`${url}/orders/user/?page=${page}&page_size=${size}`, ctx),

  rates: () => `${url}/rates/`,

  sidebar: () => `${url}/sidebar/`,

  company: (isin) => `${url}/companies/${isin}/`,

  shareholders: (isin) => `${url}/companies/${isin}/shareholders/`,

  liquidity: (isin) => `${url}/companies/${isin}/liquidity/`,

  statementOfAccount: (isin, page, size, ctx) => sortedApi(`${url}/companies/${isin}/statement_of_account/?page=${page}&page_size=${size}`, ctx),

  tradesCompany: (isin, page, size, ctx) => sortedApi(`${url}/companies/${isin}/trades/?page=${page}&page_size=${size}`, ctx),

  buyerSeller: (isin, page, size, ctx) => sortedApi(`${url}/companies/${isin}/buyer_seller/?page=${page}&page_size=${size}`, ctx),

  depot: (isin, page, size, ctx) => sortedApi(`${url}/companies/${isin}/depot/?page=${page}&page_size=${size}`, ctx),

  ordersCompany: (isin, page, size, ctx) => sortedApi(`${url}/companies/${isin}/orders/?page=${page}&page_size=${size}&ordering=-price`, ctx),

  depotPieChart: (isin) => `${url}/companies/${isin}/depot/slim/`,

  bondsCompany: (isin, page, size, ctx) => sortedApi(`${url}/companies/${isin}/bond/?page=${page}&page_size=${size}`, ctx),

  articlesCompany: (isin, page, size, ctx) => sortedApi(`${url}/social/companies/${isin}/articles/?page=${page}&page_size=${size}`, ctx),

  past_key_figures: (isin) => `${url}/stats/${isin}/key_figures/`,

  login: () => `${url}/social/login/`,

  register: () => `${url}/social/register/`,

  notifications: (page, size, ctx) => sortedApi(`${url}/social/notifications/?page=${page}&page_size=${size}`, ctx),

  notificationDetail: (id) => `${url}/social/notifications/${id}/`,

  messages: (page, size, ctx) => sortedApi(`${url}/social/conversations/?page=${page}&page_size=${size}`, ctx),

  messageDetail: (id, page, size, ctx) => sortedApi(`${url}/social/conversations/${id}/?page=${page}&page_size=${size}`, ctx),

  articles: (page, size, ctx) => sortedApi(`${url}/social/articles/?page=${page}&page_size=${size}`, ctx),

  threads: (page, size, ctx) => sortedApi(`${url}/social/threads/?page=${page}&page_size=${size}`, ctx),

  thread: (id, page, size, ctx) => sortedApi(`${url}/social/threads/${id}/posts/?page=${page}&page_size=${size}`, ctx),

  userLookup: (name) => `${url}/social/users/lookup/${name}/`,

  user: (id) => `${url}/social/users/${id}/`,

  profile: (userId) => `${url}/social/profile/${userId}/`,

  unread: () => `${url}/social/unread/`,

  fonds: (page, size, ctx) => sortedApi(`${url}/fonds/?page=${page}&page_size=${size}`, ctx),

  fond: (id) => `${url}/fonds/${id}/`,

  fondSlim: (id) => `${url}/fonds/${id}/slim/`,

  fondProfile: (id) => `${url}/fonds/${id}/profile/`,

  fondApplication: (id, page, size) => `${url}/fonds/${id}/applications/?page=${page}&page_size=${size}`,

  fondApplicationDelete: (fondID, applicationID) => `${url}/fonds/${fondID}/applications/${applicationID}/`,

  fondThreads: (fondID, page, size, ctx) => sortedApi(`${url}/fonds/${fondID}/threads/?page=${page}&page_size=${size}`, ctx),

  fondThread: (fondID, threadID, page, size, ctx) => sortedApi(`${url}/fonds/${fondID}/threads/${threadID}/?page=${page}&page_size=${size}`, ctx),

  fondsUserData: () => `${url}/fonds/user_data/`,

};

export default Api;
