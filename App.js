import React from 'react';
import {StyleSheet, View} from 'react-native';
import {createStackNavigator} from '@react-navigation/stack';
import {NavigationContainer} from '@react-navigation/native';
import HomeScreen from './src/home-screen';
import {Button} from 'react-native-elements';
import Icon from 'react-native-vector-icons/FontAwesome';
import {withAuthenticator} from 'aws-amplify-react-native';
import {Auth} from 'aws-amplify';

const App: () => React$Node = () => {
  const Stack = createStackNavigator();
  return (
    <>
      <NavigationContainer>
        <Stack.Navigator initialRouteName="Home">
          <Stack.Screen
            name="Home"
            component={HomeScreen}
            options={({navigation}) => ({
              title: 'My Translator',
              headerStyle: {
                backgroundColor: '#808080',
              },
              headerLeft: () => (
                <View style={styles.logOutBtn}>
                  <Button
                    icon={<Icon name="sign-out" size={25} color="#000000" />}
                    onPress={() => Auth.signOut()}
                    type="clear"
                  />
                </View>
              ),
            })}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </>
  );
};
const styles = StyleSheet.create({
  addButton: {
    marginRight: 20,
  },
  logOutBtn: {
    marginLeft: 10,
  },
});

export default withAuthenticator(App);
