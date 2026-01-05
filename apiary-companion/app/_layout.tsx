import { Stack } from 'expo-router';
import { useEffect, useState } from 'react';
import { ActivityIndicator, View } from 'react-native';
import db from '../src/database';
import { seedService } from '../src/services/seedService';

export default function RootLayout() {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    async function prepare() {
      try {
        await db.init();

        // Check if database has data, if not seed it
        const result = await db.getFirstAsync<{ count: number }>(
          'SELECT COUNT(*) as count FROM users'
        );

        if (result?.count === 0) {
          await seedService.seedDemoData();
        }

        setIsReady(true);
      } catch (error) {
        console.error('Failed to initialize app:', error);
      }
    }

    prepare();
  }, []);

  if (!isReady) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#FFA500" />
      </View>
    );
  }

  return (
    <Stack
      screenOptions={{
        headerStyle: {
          backgroundColor: '#FFA500',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <Stack.Screen name="index" options={{ title: 'My Apiaries' }} />
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="apiary/[id]" options={{ title: 'Apiary Details' }} />
      <Stack.Screen name="hive/[id]" options={{ title: 'Hive Details' }} />
      <Stack.Screen name="inspection/create" options={{ title: 'New Inspection' }} />
      <Stack.Screen name="inspection/[id]" options={{ title: 'Inspection Details' }} />
      <Stack.Screen name="inspection/review" options={{ title: 'Review Findings' }} />
    </Stack>
  );
}
