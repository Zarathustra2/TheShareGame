import Vue from 'vue';
import Vuex from 'vuex';
import Service from '@/service/service';
import Api from '@/service/api';
import Axios from 'axios';

Vue.use(Vuex);


// A store to hold events received from websockets
//
// For instance, the ChatBox Componenent will consume all chat messages received
// from websockets.
//
// The Navbar will use a new message/notficition event to update
// the unread messages counter.
//
const store = new Vuex.Store({
  state: {

    // Array holding received chat messages from a websocket
    chatMessages: [],

    // The maximum amount of messages the array should contain
    maximumMessages: 5,

    // The websocket connection of the client
    ws: null,

    unreadMessages: 0,

    unreadNotifications: 0,

    // The fond data of the user. There are 3 values this variable can have:
    //  1. undefined => No Data has been fetched
    //  2. null => The user is not a member of a fond
    //  3. object => The user is a member in a fond
    fond: undefined,
  },

  mutations: {
    newChatMsg(state, msg) {
      const date = new Date(msg.time);
      const minutes = date.getMinutes();

      let minutesStr = `${minutes}`;
      if (minutes >= 0 && minutes <= 9) {
        minutesStr = `0${minutes}`;
      }

      msg.time = `${date.getHours()}:${minutesStr}`;

      if (state.chatMessages.length >= state.maximumMessages) {
        state.chatMessages.shift();
      }

      state.chatMessages.push(msg);
    },

    setMaxMsg(state, num) {
      state.maximumMessages = num;
    },

    sendChatMsg(state, data) {
      if (state.ws !== null && Service.isAuthenticated()) {
        state.ws.send(JSON.stringify(data));
      }
    },

    setWebsocket(state, ws) {
      state.ws = ws;
    },

    setUnreadMessages(state, num) {
      state.unreadMessages = num;
    },

    setUnreadNotifications(state, num) {
      state.unreadNotifications = num;
    },

    setFond(state, data) {
      state.fond = data;
    },

  },

  getters: {
    getMsg(state) {
      return state.chatMessages;
    },
    getUnread(state) {
      const { unreadMessages, unreadNotifications } = state;
      return { unreadMessages, unreadNotifications };
    },
    getTotalUnread(state) {
      const { unreadMessages, unreadNotifications } = state;
      return unreadMessages + unreadNotifications;
    },

    getFond(state) {
      return state.fond;
    },

    hasFond(state) {
      return state.fond !== null && state.fond !== undefined;
    },

    isFondLeader(state) {
      if (state.fond === null || state.fond === undefined) {
        return false;
      }

      return state.fond.leader;
    },

  },

  actions: {

    /**
     * Vuex actions which calls the api and sets the unread messages
     * and notifications
     *
     */
    unread({ commit }) {
      if (Service.isAuthenticated()) {
        Service.checkAxiosToken();
        Axios.get(Api.unread()).then((r) => {
          // eslint-disable-next-line
          const { unread_messages, unread_notifications } = r.data;

          // eslint-disable-next-line
          if (unread_messages === undefined) {
            console.error('unread_messages is null!');
          }

          // eslint-disable-next-line
          if (unread_notifications === undefined) {
            console.error('unread_notifications is null!');
          }

          commit('setUnreadMessages', unread_messages);
          commit('setUnreadNotifications', unread_notifications);
        }).catch((err) => {
          console.error(err);
        });
      }
    },

    /**
     * Vuex actions which calls the api and sets the fond data of the user
     *
     */
    fondData({ commit, state }) {
      // If the state is not undefined, the data has already been fetched and
      // we do not need to fetch the data again.
      if (Service.isAuthenticated() && state.fond === undefined) {
        Service.checkAxiosToken();

        Axios.get(Api.fondsUserData()).then((r) => {
          commit('setFond', r.data);
        }).catch((err) => {
          if (err.response.status === 404) {
            commit('setFond', null);
          } else {
            console.error(err);
          }
        }).catch((err) => {
          console.error(err);
        });
      }
    },
  },

});

export default store;
